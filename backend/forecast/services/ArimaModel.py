import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima   # thêm thư viện này để chọn tham số tối ưu

CLEANED_PARQUET = Path(__file__).parent.parent.parent / "core" / "data" / "cleaned_covid_data.parquet"


def predict_covid_arima(location, start_date_str, forecast_days=30, user_stringency=None, metric='new_cases_smoothed'):
    # --- 1. Đọc dữ liệu ---
    df = pd.read_parquet(CLEANED_PARQUET)
    df['date'] = pd.to_datetime(df['date'])

    df_nation = df[df['location'] == location].copy()
    selected_date = pd.to_datetime(start_date_str)

    # --- 2. Lấy dữ liệu train và actual ---
    train_df = df_nation[df_nation['date'] < selected_date].tail(365).copy()  # lấy nhiều hơn để ARIMA học tốt hơn
    actual_df = df_nation[df_nation['date'] >= selected_date].head(forecast_days).copy()

    # --- 3. Kiểm tra dữ liệu đầu vào ---
    if train_df[metric].isnull().all():
        raise ValueError(f"Không có dữ liệu {metric} cho {location} trước ngày {start_date_str}")

    # --- 4. Huấn luyện ARIMA ---
    train_series = train_df[metric].fillna(0)

    # Dùng auto_arima để chọn tham số tốt nhất
    try:
        auto_model = auto_arima(train_series, seasonal=False, stepwise=True, suppress_warnings=True)
        order = auto_model.order
    except Exception:
        order = (2, 1, 2)  # fallback nếu auto_arima lỗi

    model = ARIMA(train_series, order=order)
    fitted_model = model.fit()

    periods = len(actual_df) if not actual_df.empty else forecast_days
    forecast_values = fitted_model.forecast(steps=periods).clip(lower=0)

    # --- 5. TÍNH TOÁN KỊCH BẢN (SCENARIO) ---
    current_relax = train_df['relaxation_index'].iloc[-1] if 'relaxation_index' in train_df.columns else 50
    current_stringency = 100 - current_relax

    target_stringency = float(user_stringency) if user_stringency is not None else current_stringency
    stringency_diff = target_stringency - current_stringency
    sensitivity_factor = 0.015
    multiplier = 1.0 - (stringency_diff * sensitivity_factor)
    multiplier = max(0.05, min(multiplier, 3.0))

    # --- 6. TỔNG HỢP KẾT QUẢ ---
    forecast_df = pd.DataFrame({
        'ds': pd.date_range(start=selected_date, periods=periods),
        'yhat_baseline': forecast_values,
        'baseline_lower': forecast_values * 0.9,
        'baseline_upper': forecast_values * 1.1,
        'yhat_scenario': forecast_values * multiplier,
        'y_actual': actual_df[metric].values if not actual_df.empty else [None] * periods
    })

    # --- 7. Tính toán MAPE/MAE ---
    temp_eval = forecast_df.dropna(subset=['y_actual']).copy()
    mape, mae = None, None
    if not temp_eval.empty:
        mae = float(np.mean(np.abs(temp_eval['y_actual'] - temp_eval['yhat_baseline'])))
        temp_eval_mape = temp_eval[temp_eval['y_actual'] > 0]
        if not temp_eval_mape.empty:
            mape = float(np.mean(np.abs(
                (temp_eval_mape['y_actual'] - temp_eval_mape['yhat_baseline']) / temp_eval_mape['y_actual'])) * 100)

    return forecast_df, mape, mae, current_stringency
