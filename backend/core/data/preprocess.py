# backend/covid_app/data/preprocess.py
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from update_data import download_latest

RAW_FILE = Path(__file__).parent / "owid-covid-data.csv"
CLEANED_PARQUET = Path(__file__).parent / "cleaned_covid_data.parquet"


def preprocess_and_save():
    print("Bắt đầu preprocessing...")

    df = pd.read_csv(RAW_FILE)
    df = df.drop_duplicates(subset=['location', 'date'])
    df['date'] = pd.to_datetime(df['date'])
    # sap xep time-seri cho mot quoc gia
    df = df.sort_values(['location', 'date'])

    # Loại bỏ các dòng tổng hợp không cần thiết
    exclude = ['World', 'Europe', 'Asia', 'European Union', 'International',
               'High income', 'Low income', 'Upper middle income', 'Lower middle income',
               'Africa', 'North America', 'South America', 'Oceania']
    df = df[~df['location'].isin(exclude)]

    # Forward fill + fillna 0
    # Ép các giá trị âm về 0 (đôi khi dữ liệu gốc có số âm do hiệu chỉnh)
    for col in ['new_cases', 'new_deaths']:
        if col in df.columns:
            df[col] = df[col].clip(lower=0)

    # dùng hàm pandas lấy các cột có kieu du lieu la number
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # group theo quoc gia
    # neu gia tri bi trong thi lay gia tri phia truoc dien vao
    df[numeric_cols] = df.groupby('location')[numeric_cols].ffill()
    # truong hop phia truoc o trong cung khong co du lieu NaN thi dien 0 vao
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Tạo smoothed columns
    df['new_cases_smoothed'] = df.groupby('location')['new_cases'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    df['new_deaths_smoothed'] = df.groupby('location')['new_deaths'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )

    # Tạo hoặc lưu vào file.parquet để tăng tốc độ đọc hay vì .csv
    df.to_parquet(CLEANED_PARQUET, index=False, compression='gzip')

    size_mb = CLEANED_PARQUET.stat().st_size // 1024 // 1024
    print(f"HOÀN TẤT!")


if __name__ == "__main__":
    # download_latest()
    preprocess_and_save()
