import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

# Đường dẫn chung
CLEANED_PARQUET = Path(__file__).parent.parent.parent / "core" / "data" / "cleaned_covid_data.parquet"


def load_data_from_parquet() -> pd.DataFrame:
    if not CLEANED_PARQUET.exists():
        raise FileNotFoundError(f"Lỗi: Không tìm thấy file {CLEANED_PARQUET}. Vui lòng chạy preprocess.py trước.")
    return pd.read_parquet(CLEANED_PARQUET)


def get_latest_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(by='date', ascending=False).drop_duplicates(subset=['location'])


class SummaryService:
    """
    Service cho Insight 1: Tổng quan COVID-19 tại một quốc gia.
    """
    def __init__(self):
        df_raw = load_data_from_parquet()
        self.df_latest = get_latest_data(df_raw)

    def _normalize(self, text: str) -> str:
        """Chuẩn hóa tên quốc gia để matching dễ dàng."""
        return "".join(text.lower().split())

    def get_country_summary(self, location: str) -> Optional[Dict[str, Any]]:
        if not location:
            return None

        df = self.df_latest
        location_norm = self._normalize(location)

        # Các cách match theo thứ tự ưu tiên
        candidates = [
            df['location'] == location,  # Exact
            df['location'].str.strip().str.lower() == location.strip().lower(),  # Case-insensitive + strip
            df['location'].apply(self._normalize) == location_norm,  # Bỏ hết space
            df['location'].str.contains(location, case=False, na=False),  # Partial contains
        ]

        # Fallback đặc biệt cho Việt Nam (thường bị khác tên)
        if location_norm in ["vietnam", "viet nam", "việtnam", "việt nam"]:
            candidates.append(df['location'] == "Vietnam")

        for condition in candidates:
            row_df = df[condition]
            if not row_df.empty:
                row = row_df.iloc[0]
                break
        else:
            return None  # Không tìm thấy

        population = row.get("population", 1) or 1

        # Tính tổng từ per_million
        total_cases = int((row.get("total_cases_per_million", 0) or 0) * population / 1_000_000)
        total_deaths = int((row.get("total_deaths_per_million", 0) or 0) * population / 1_000_000)

        # Tỉ lệ tiêm chủng (ưu tiên fully vaccinated)
        vaccination_rate = (
            row.get("people_fully_vaccinated_per_hundred", 0) or
            row.get("total_vaccinations_per_hundred", 0) or
            row.get("people_vaccinated_per_hundred", 0) or 0
        )

        # Tỉ lệ tử vong
        mortality_rate = round((total_deaths / total_cases * 100), 2) if total_cases > 0 else 0

        return {
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "mortality_rate": mortality_rate,
            "vaccination_rate": round(vaccination_rate, 2)
        }