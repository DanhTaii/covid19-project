import pandas as pd
import numpy as np
from analysis.services.FactorCorrelationService import load_data_from_parquet, get_latest_data


class MortalityRatioService:
    """
    Service xử lý logic cho Insight 3: Mức độ Nghiêm trọng.
    Đã tối giản: Chỉ tập trung vào hiển thị bản đồ và số liệu của quốc gia được chọn.
    """

    def __init__(self):
        # Tải dữ liệu và lấy ngày mới nhất
        df_raw = load_data_from_parquet()
        self.df_latest = get_latest_data(df_raw)
        self.TARGET_COL = 'total_deaths_per_million'

    def get_choropleth_data(self, location: str = None) -> list:
        """
        Lấy dữ liệu để vẽ bản đồ.
        - Nếu location = 'All Countries': Trả về dữ liệu toàn cầu (tô màu tất cả).
        - Nếu location = 'Vietnam': Chỉ trả về 1 dòng dữ liệu của VN (bản đồ chỉ tô màu VN).
        """
        # Copy để không ảnh hưởng dữ liệu gốc
        df_filtered = self.df_latest.copy()

        # 1. Logic lọc: Chỉ giữ lại đúng quốc gia người dùng chọn
        if location and location != 'All Countries':
            df_filtered = df_filtered[df_filtered['location'] == location]

        # 2. Chọn cột cần thiết và loại bỏ dữ liệu lỗi
        df_map = df_filtered[['iso_code', 'location', self.TARGET_COL, 'date']].dropna(
            subset=[self.TARGET_COL, 'iso_code']
        )

        return df_map.to_dict('records')

    def get_selected_country_stat(self, location: str = None) -> dict:
        """
        Hàm phụ trợ: Lấy con số cụ thể của quốc gia đang chọn để hiển thị lên thẻ số (Metric).
        """
        df_filtered = self.df_latest.copy()

        # Nếu chọn 1 quốc gia
        if location and location != 'All Countries':
            row = df_filtered[df_filtered['location'] == location]
            if not row.empty:
                val = row.iloc[0][self.TARGET_COL]
                return {
                    'location': location,
                    'value': f"{val:,.0f}",  # Format số: 1,234
                    'label': 'Total Deaths / Million'
                }

        # Nếu chọn All Countries -> Tính trung bình toàn cầu
        global_avg = df_filtered[self.TARGET_COL].mean()
        return {
            'location': 'Global Average',
            'value': f"{global_avg:,.0f}",
            'label': 'Average Deaths / Million'
        }