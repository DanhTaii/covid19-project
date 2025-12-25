import pandas as pd
from prophet import Prophet
from pathlib import Path
CLEANED_PARQUET = Path(__file__).parent.parent.parent / "covid_app" / "data" / "cleaned_covid_data.parquet"


def predict_covid(location, start_date_str, forecast_days=30, metric='new_cases_smoothed'):

    # đọc dữ liệu từ dữ liệu sạch
    df = pd.read_parquet(CLEANED_PARQUET)

    # 2 lọc dữ liệu quốc gia
    # lấy quốc gia từ df ra so sánh với quốc gia người dùng chọn
    df_nation = df[df['location'] == location].copy()

    # lay du lieu tu ngay truoc ngay nguoi dung chon de huan luyen
    selected_date = pd.to_datetime(start_date_str)
    train_df = df_nation[df_nation['date'] < selected_date].copy()

    # 3 chuẩn bị file cho prophet độc
    # Chuẩn bị bảng cho Prophet
    df_prophet = train_df[['date', metric]].copy()
    df_prophet.columns = ['ds', 'y']

    # 4 khởi tạo mô hình
    model = Prophet(
        interval_width=0.80,
        changepoint_prior_scale=0.05,
        weekly_seasonality=True,
        yearly_seasonality=False
    )



    # 5. huan luyen mo hinh
    model.fit(df_prophet)

    # 6. tao cot ds
    # start = ngay nguoi dung chon - periods là so luong ngay du bao
    future_dates = pd.date_range(start=selected_date, periods=forecast_days)
    future = pd.DataFrame({'ds': future_dates})

    # 7. Dự báo
    forecast = model.predict(future)

    # 8. Hậu xử lý kết quả
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    result[['yhat', 'yhat_lower', 'yhat_upper']] = result[['yhat', 'yhat_lower', 'yhat_upper']].clip(lower=0).round(
        0).astype(int)

    return result

