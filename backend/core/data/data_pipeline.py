import numpy as np
import  pandas as pd

from backend.core.data.preprocess import CLEANED_PARQUET

def prepare_for_training(split_date='2024-01-01', target_shift=3):
    df = pd.read_parquet(CLEANED_PARQUET)
    # Chỉ giữ lại các cột cần thiết
    df = df[['location', 'date', 'population', 'new_deaths_smoothed', 'new_cases_smoothed']]

    # --- 1. Định nghĩa Target (y) ---
    # Tức là: new_deaths_smoothed 3 ngày sau.
    # Shift(-3) sẽ dịch chuyển giá trị của cột 'new_deaths_smoothed' lên 3 hàng.
    k = 3
    df['target_new_deaths'] = df.groupby('location')['new_deaths_smoothed'].shift(-k)

    # Xóa các dòng mà không thể tính target (các dòng cuối cùng của mỗi quốc gia)
    df.dropna(subset=['target_new_deaths'], inplace=True)

    # Định nghĩa các features (X) và target (y)
    # X: Các đặc trưng (ví dụ: location, population, các cột smoothed)
    X = df[['location', 'date', 'population', 'new_deaths_smoothed', 'new_cases_smoothed']]
    # y: Mục tiêu dự đoán (target)
    y = df['target_new_deaths']

    # Lưu ý: Cột 'date' được giữ lại trong X để dùng cho việc chia tập.