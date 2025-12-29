import pandas as pd
import numpy as np
from prophet import Prophet
from pathlib import Path

CLEANED_PARQUET = Path(__file__).parent.parent.parent / "covid_app" / "data" / "cleaned_covid_data.parquet"


def predict_covid(location, start_date_str, forecast_days=30, metric='new_cases_smoothed'):
    # 1. Đọc dữ liệu
    df = pd.read_parquet(CLEANED_PARQUET)
    df['date'] = pd.to_datetime(df['date'])
    df_nation = df[df['location'] == location].copy()
    selected_date = pd.to_datetime(start_date_str)


    train_df = df_nation[df_nation['date'] < selected_date].tail(90).copy()
    actual_df = df_nation[df_nation['date'] >= selected_date].head(forecast_days).copy()

    # 3. LOG TRANSFORMATION: Biến đổi dữ liệu về dạng Log để nén các cú sốc
    # Công thức: y_log = log(y + 1)
    train_df['y_log'] = np.log1p(train_df[metric])
    df_prophet = train_df[['date', 'y_log']].rename(columns={'date': 'ds', 'y_log': 'y'})

    # 4. Cấu hình Model "Siêu linh hoạt"
    model = Prophet(
        interval_width=0.95,
        changepoint_prior_scale=0.8,  # Đẩy lên mức tối đa để cực kỳ nhạy bén
        seasonality_prior_scale=0.1,  # Giảm seasonality để tập trung hoàn toàn vào Trend
        growth='linear',
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    model.fit(df_prophet)

    # 5. Dự báo trên thang Log
    periods = len(actual_df) if not actual_df.empty else forecast_days
    future = model.make_future_dataframe(periods=periods, include_history=False)
    future['ds'] = pd.date_range(start=selected_date, periods=periods)

    forecast_log = model.predict(future)

    # 6. REVERSE LOG: Chuyển dữ liệu từ Log về con số thực tế
    # Công thức: y = exp(y_log) - 1
    forecast = forecast_log[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        forecast[col] = np.expm1(forecast[col])

    # 7. Gộp kết quả
    actual_compare = actual_df[['date', metric]].rename(columns={'date': 'ds', metric: 'y_actual'})
    comparison_df = pd.merge(forecast, actual_compare, on='ds', how='left')

    # Làm tròn
    cols = ['yhat', 'yhat_lower', 'yhat_upper', 'y_actual']
    comparison_df[cols] = comparison_df[cols].clip(lower=0).round(0)

    # 8. Tính MAPE
    temp_eval = comparison_df.dropna(subset=['y_actual']).copy()
    temp_eval = temp_eval[temp_eval['y_actual'] > 0]

    mape = None
    if not temp_eval.empty:
        mape = np.mean(np.abs((temp_eval['y_actual'] - temp_eval['yhat']) / temp_eval['y_actual'])) * 100

    return comparison_df, mape