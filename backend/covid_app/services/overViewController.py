import os
import pandas as pd
import plotly.express as px

class OverViewController:
    def __init__(self, parquet_path: str):
        self.df = pd.read_parquet(parquet_path)

        # Chuẩn hóa cột date
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

    # hiển thị bản đồ thế giới theo chế độ
    # mặc định là chế độ ca nhiễm
    def world_map(self, mode: str = "cases"):
        if mode == "deaths":
            value_col = "total_deaths"
            title = "Total COVID-19 Deaths by Country"
            color_scale = "Blues"
        else:
            value_col = "total_cases"
            title = "Total COVID-19 Cases by Country"
            color_scale = "Reds"

        # Tính tổng theo quốc gia
        df_total = self.df.groupby("location", as_index=False)[value_col].max()

        # Vẽ bản đồ
        fig = px.choropleth(
            df_total,
            locations="location",
            locationmode="country names",
            color=value_col,
            color_continuous_scale=color_scale,
            title=title,
        )
        fig.update_geos(projection_type="natural earth")
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        return fig
