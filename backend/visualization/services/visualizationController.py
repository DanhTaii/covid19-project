import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as date

# tạo lớp để xử lý
class CovidVisualizerOO:
    def __init__(self, parquet_path: str):
        # Load dữ liệu Parquet
        self.df = pd.read_parquet(parquet_path)

        # Chuẩn hóa cột date
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

        # Xử lý thiếu dữ liệu
        for col in ["new_cases", "new_deaths"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna(0)

    # lấy danh sách quốc gia có trong dữ liệu
    def get_available_countries(self):
        return sorted(self.df["location"].dropna().unique())

    # lấy dữ liệu của quốc gia đó
    def filter_country(self, country: str) -> pd.DataFrame:
        return self.df[self.df["location"] == country]

    # vẽ biểu đồ số ca nhiễm
    def plot_cases(self, country: str):
        data = self.filter_country(country)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data["date"], data["new_cases"], color="blue", label="New Cases")

        # Định dạng trục x hiển thị năm
        ax.xaxis.set_major_locator(date.YearLocator())
        ax.xaxis.set_major_formatter(date.DateFormatter('%Y'))

        ax.set(title=f"COVID-19 New Cases in {country}", xlabel="Year", ylabel="Cases")
        ax.legend()
        fig.autofmt_xdate()
        fig.subplots_adjust(bottom=0.2)
        return fig

    # vẽ biểu đồ số ca chết
    def plot_deaths(self, country: str):
        """Vẽ biểu đồ số ca tử vong mới theo thời gian."""
        data = self.filter_country(country)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data["date"], data["new_deaths"], color="red", label="New Deaths")

        # Định dạng trục x hiển thị năm
        ax.xaxis.set_major_locator(date.YearLocator())
        ax.xaxis.set_major_formatter(date.DateFormatter('%Y'))

        ax.set(title=f"COVID-19 New Deaths in {country}", xlabel="Year", ylabel="Deaths")
        ax.legend()
        fig.autofmt_xdate()
        fig.subplots_adjust(bottom=0.2)
        return fig
