import pandas as pd
import numpy as np
from prophet import Prophet
from pathlib import Path

CLEANED_PARQUET = Path(__file__).parent.parent.parent / "core" / "data" / "cleaned_covid_data.parquet"


def predict_covid(location, start_date_str, forecast_days=30, user_stringency=None, metric='new_cases_smoothed'):
    df = pd.read_parquet(CLEANED_PARQUET)
    df['date'] = pd.to_datetime(df['date'])

    df_nation = df[df['location'] == location].copy()
    selected_date = pd.to_datetime(start_date_str)

    # Lấy dữ liệu train và actual
    train_df = df_nation[df_nation['date'] < selected_date].tail(150).copy()
    actual_df = df_nation[df_nation['date'] >= selected_date].head(forecast_days).copy()

    # Xử lý log và chuẩn bị cho Prophet
    # Lưu ý: Ta KHÔNG cần regr_relax cho Prophet nữa, để Prophet tập trung bắt trend tự nhiên
    train_df['y_log'] = np.log1p(train_df[metric])
    df_prophet = train_df[['date', 'y_log']].rename(columns={'date': 'ds', 'y_log': 'y'})

    # --- 2. DỰ BÁO BASELINE (XU HƯỚNG TỰ NHIÊN) ---
    model = Prophet(
        interval_width=0.95,
        changepoint_prior_scale=0.05,
        seasonality_prior_scale=0.1,
        growth='linear',
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    model.fit(df_prophet)

    periods = len(actual_df) if not actual_df.empty else forecast_days
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    # Cắt lấy phần dự báo tương lai
    forecast_future = forecast.tail(periods).copy()

    # --- 3. TÍNH TOÁN KỊCH BẢN (SCENARIO) BẰNG LOGIC ĐÀN HỒI ---
    current_relax = train_df['relaxation_index'].iloc[-1]
    current_stringency = 100 - current_relax

    # Mức phong tỏa người dùng chọn
    target_stringency = float(user_stringency) if user_stringency is not None else current_stringency
    stringency_diff = target_stringency - current_stringency
    sensitivity_factor = 0.015
    multiplier = 1.0 - (stringency_diff * sensitivity_factor)
    multiplier = max(0.05, min(multiplier, 3.0))

    # --- 4. TỔNG HỢP KẾT QUẢ ---
    comparison_df = pd.DataFrame({
        'ds': forecast_future['ds'],
        'y_actual': actual_df[metric].values if not actual_df.empty else [None] * periods,

        # Baseline (Dự báo theo đà thực tế)
        'yhat_baseline': np.expm1(forecast_future['yhat']).clip(lower=0),
        'baseline_upper': np.expm1(forecast_future['yhat_upper']).clip(lower=0),
        'baseline_lower': np.expm1(forecast_future['yhat_lower']).clip(lower=0),

        # Scenario (Dự báo đã điều chỉnh theo Logic)
        'yhat_scenario': np.expm1(forecast_future['yhat']).clip(lower=0) * multiplier
    })

    # Tính toán MAPE/MAE dựa trên Baseline
    temp_eval = comparison_df.dropna(subset=['y_actual']).copy()
    mape, mae = None, None
    if not temp_eval.empty:
        mae = float(np.mean(np.abs(temp_eval['y_actual'] - temp_eval['yhat_baseline'])))
        temp_eval_mape = temp_eval[temp_eval['y_actual'] > 0]
        if not temp_eval_mape.empty:
            mape = float(np.mean(np.abs(
                (temp_eval_mape['y_actual'] - temp_eval_mape['yhat_baseline']) / temp_eval_mape['y_actual'])) * 100)

    return comparison_df, mape, mae,current_stringency