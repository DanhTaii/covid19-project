import pandas as pd
import numpy as np
from pathlib import Path

# Đường dẫn đến file Parquet đã làm sạch
CLEANED_PARQUET = Path(__file__).parent.parent.parent / "core" / "data" / "cleaned_covid_data.parquet"


def load_data_from_parquet() -> pd.DataFrame:
    """Tải DataFrame đã làm sạch từ file Parquet."""
    if not CLEANED_PARQUET.exists():
        raise FileNotFoundError(
            f"Lỗi: Không tìm thấy file đã làm sạch tại {CLEANED_PARQUET}. Vui lòng chạy preprocess.py trước.")
    return pd.read_parquet(CLEANED_PARQUET)


def get_latest_data(df: pd.DataFrame) -> pd.DataFrame:
    """Lọc dữ liệu tích lũy cuối cùng (hàng mới nhất) cho mỗi quốc gia."""
    # Giả định dữ liệu đã được làm sạch và sắp xếp theo ngày trong preprocess
    return df.sort_values(by='date', ascending=False).drop_duplicates(subset=['location'])


class FactorCorrelationService:
    """
    Service xử lý logic cho Insight 4: Phân tích Tương quan Yếu tố Rủi ro.
    Cung cấp dữ liệu cho Heatmap và Scatter Plots.
    """

    def __init__(self):
        # Tải dữ liệu thô từ Parquet
        df_raw = load_data_from_parquet()
        # Lấy dữ liệu tích lũy cuối cùng cho mỗi quốc gia
        self.df_latest = get_latest_data(df_raw)

        self.CORR_COLS = [
            'total_deaths_per_million',  # Biến mục tiêu (Trục Y)
            'median_age',
            'population_density',
            'total_vaccinations_per_hundred'  # Có thể là total_vaccinations_per_hundred
        ]

    def get_correlation_matrix(self) -> dict:
        """
        Tính toán ma trận tương quan Pearson cho Heatmap.
        Trả về dưới dạng dictionary để dễ dàng chuyển đổi sang JSON/giao diện người dùng.
        """
        # Bỏ các hàng có NaN trong các cột tương quan (quan trọng)
        df_corr = self.df_latest[self.CORR_COLS].dropna()

        # Tính toán ma trận tương quan
        correlation_matrix = df_corr.corr()

        # Chuyển thành dictionary để dễ dàng gửi đi qua API
        return correlation_matrix.to_dict()

    def get_scatter_data(self) -> dict:
        """
        Trích xuất dữ liệu cho 2 Biểu đồ Phân tán chính (Tuổi vs Tử vong, Tiêm chủng vs Tử vong).
        """
        # Chọn các cột cần thiết, bỏ NaN trong các cột phân tích
        df_scatter = self.df_latest[self.CORR_COLS + ['location']].dropna(subset=self.CORR_COLS)

        # 1. Tuổi vs Tử vong
        age_vs_deaths = df_scatter[['location', 'median_age', 'total_deaths_per_million']].to_dict('records')

        # 2. Tiêm chủng vs Tử vong
        vaccine_vs_deaths = df_scatter[
            ['location', 'total_vaccinations_per_hundred', 'total_deaths_per_million']].to_dict('records')

        # Hàm ý: Khi median_age cao, total_deaths_per_million có xu hướng cao hơn.

        return {
            'age_vs_deaths': age_vs_deaths,
            'vaccine_vs_deaths': vaccine_vs_deaths
        }