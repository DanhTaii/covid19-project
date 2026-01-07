import pandas as pd
import numpy as np
from prophet import Prophet
from pathlib import Path

CLEANED_PARQUET = Path(__file__).parent.parent.parent / "core" / "data" / "cleaned_covid_data.parquet"

def predict_covid(location, start_date_str, forecast_days=30, metric='new_cases_smoothed'):
    df = pd.read_parquet(CLEANED_PARQUET)

    df_nation = df[df['location'] == location].copy()
    selected_date = pd.to_datetime(start_date_str)

    train_df = df_nation[df_nation['date'] < selected_date].tail(90).copy()
    actual_df = df_nation[df_nation['date'] >= selected_date].head(forecast_days).copy()

    train_df['y_log'] = np.log1p(train_df[metric])
    df_prophet = train_df[['date', 'y_log']].rename(columns={'date': 'ds', 'y_log': 'y'})

    model = Prophet(
        interval_width=0.95,
        changepoint_prior_scale=0.8,
        seasonality_prior_scale=0.1,
        growth='linear',
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False
    )
    model.fit(df_prophet)

    periods = len(actual_df) if not actual_df.empty else forecast_days
    future = model.make_future_dataframe(periods=periods, include_history=False)
    future['ds'] = pd.date_range(start=selected_date, periods=periods)

    forecast_log = model.predict(future)

    forecast = forecast_log[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        forecast[col] = np.expm1(forecast[col])

    actual_compare = actual_df[['date', metric]].rename(columns={'date': 'ds', metric: 'y_actual'})
    comparison_df = pd.merge(forecast, actual_compare, on='ds', how='left')

    cols = ['yhat', 'yhat_lower', 'yhat_upper', 'y_actual']
    comparison_df[cols] = comparison_df[cols].clip(lower=0).round(0)

    temp_eval = comparison_df.dropna(subset=['y_actual']).copy()

    mape = None
    mae = None

    if not temp_eval.empty:
        mae = np.mean(np.abs(temp_eval['y_actual'] - temp_eval['yhat']))
        temp_eval_mape = temp_eval[temp_eval['y_actual'] > 0]
        if not temp_eval_mape.empty:
            mape = np.mean(np.abs((temp_eval_mape['y_actual'] - temp_eval_mape['yhat']) / temp_eval_mape['y_actual'])) * 100

    return comparison_df, mape, mae