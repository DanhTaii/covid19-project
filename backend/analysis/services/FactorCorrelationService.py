import pandas as pd
import numpy as np
from pathlib import Path

from core.data.update_data import load_data_from_parquet, get_latest_data

class FactorCorrelationService:

    def __init__(self):
        df_raw = load_data_from_parquet()
        self.df_latest = get_latest_data(df_raw)

        self.CORR_COLS = [
            'total_deaths_per_million',  # Biến mục tiêu (Trục Y)
            'median_age',
            'population_density',
            'total_vaccinations_per_hundred'
        ]

    def get_correlation_matrix(self) -> dict:
        df_corr = self.df_latest[self.CORR_COLS].dropna()

        correlation_matrix = df_corr.corr()

        return correlation_matrix.to_dict()

    def get_scatter_data(self) -> dict:
        df_scatter = self.df_latest[self.CORR_COLS + ['location']].dropna(subset=self.CORR_COLS)

        age_vs_deaths = df_scatter[['location', 'median_age', 'total_deaths_per_million']].to_dict('records')

        vaccine_vs_deaths = df_scatter[
            ['location', 'total_vaccinations_per_hundred', 'total_deaths_per_million']].to_dict('records')

        return {
            'age_vs_deaths': age_vs_deaths,
            'vaccine_vs_deaths': vaccine_vs_deaths
        }