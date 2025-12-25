import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

from core.data.update_data import load_data_from_parquet, get_latest_data

class TransmissionRateService:
    def __init__(self):
        # Tải dữ liệu thô
        self.df_raw = load_data_from_parquet()
        # Lấy dữ liệu mới nhất
        self.df_latest = get_latest_data(self.df_raw)

    def get_transmission_data(self, location: str):
        # Copy dữ liệu quốc gia được chọn
        history_df = self.df_raw[self.df_raw['location'] == location].copy()

        # Chuyển ngày tháng sang String để người đọc
        history_df['date'] = history_df['date'].astype(str)

        # # Chọn các cột cần thiết, loại bỏ giá trị rỗng để biểu đồ không bị ngắt quãng
        trend_data = history_df[['date', 'new_cases_smoothed_per_million']].dropna().to_dict(orient='records')

        return trend_data