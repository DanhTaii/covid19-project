import os
import pandas as pd
import plotly.express as px
from django.conf import settings

class OverViewController:
    def __init__(self, parquet_path: str):
        self.df = pd.read_parquet(parquet_path)
        if "date" in self.df.columns:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

    def world_map(self, mode: str = "cases"):
        if mode == "deaths":
            value_col = "total_deaths"
            title = "Total COVID-19 Deaths by Country"
            color_scale = "Blues"
        else:
            value_col = "total_cases"
            title = "Total COVID-19 Cases by Country"
            color_scale = "Reds"

        df_total = self.df.groupby("location", as_index=False)[value_col].max()

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

    def global_trends(self):
        df_global = self.df.groupby("date", as_index=False)[["total_cases", "total_deaths"]].sum()
        return {
            "dates": df_global["date"].dt.strftime("%Y-%m-%d").tolist(),
            "cases": df_global["total_cases"].fillna(0).astype(int).tolist(),
            "deaths": df_global["total_deaths"].fillna(0).astype(int).tolist(),
        }

def get_world_map_data(mode: str = "cases"):
    parquet_path = os.path.join(settings.BASE_DIR, "core", "data", "cleaned_covid_data.parquet")
    controller = OverViewController(parquet_path)

    if mode not in ["cases", "deaths"]:
        mode = "cases"

    df = pd.read_parquet(parquet_path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if mode == "deaths":
        value_col = "total_deaths"
        title = "Total COVID-19 Deaths by Country"
    else:
        value_col = "total_cases"
        title = "Total COVID-19 Cases by Country"

    df_total = df.groupby("location", as_index=False)[value_col].max()

    return {
        "title": title,
        "locations": df_total["location"].tolist(),
        "values": df_total[value_col].fillna(0).round(0).astype(int).tolist(),
        "mode": mode,
        "global_trends": controller.global_trends()
    }
