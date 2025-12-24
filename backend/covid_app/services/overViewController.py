import os
import pandas as pd
import plotly.express as px

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

    def top10_countries(self, mode: str = "cases"):
        if mode == "deaths":
            value_col = "total_deaths"
            title = "Top 10 Countries by COVID-19 Deaths"
        else:
            value_col = "total_cases"
            title = "Top 10 Countries by COVID-19 Cases"

        if value_col not in self.df.columns:
            return {
                "title": title,
                "countries": [],
                "values": []
            }

        df_total = self.df.groupby("location", as_index=False)[value_col].max()
        df_top10 = df_total.sort_values(by=value_col, ascending=False).head(10)

        return {
            "title": title,
            "countries": df_top10["location"].fillna("Unknown").tolist(),
            "values": df_top10[value_col].fillna(0).astype(int).tolist()
        }