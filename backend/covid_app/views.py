from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import pandas as pd
import os
from django.conf import settings

class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })

class AnalysisAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Huee",
            "predicted_cases": [100, 120, 150, 180]
        })
class VisualizationAPIView(APIView):
    def get(self, request):
        return Response({})

class OverviewAPIView(APIView):
    def get(self, request):
        return Response({})


class WorldMapAPIView(APIView):
    def get(self, request):
        mode = request.query_params.get('mode', 'cases')  # ?mode=cases hoặc deaths

        parquet_path = os.path.join(settings.BASE_DIR, "covid_app", "data", "cleaned_covid_data.parquet")
        df = pd.read_parquet(parquet_path)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        if mode == "deaths":
            value_col = "total_deaths"
            title = "Total COVID-19 Deaths by Country"
        else:
            value_col = "total_cases"
            title = "Total COVID-19 Cases by Country"

        # Gom nhóm theo quốc gia, lấy giá trị lớn nhất (mới nhất)
        df_total = df.groupby("location", as_index=False)[value_col].max()

        # Chuẩn bị dữ liệu cho Plotly (React sẽ nhận đúng định dạng này)
        data = {
            "title": title,
            "locations": df_total["location"].tolist(),
            "values": df_total[value_col].fillna(0).round(0).astype(int).tolist(),
            "mode": mode
        }

        return Response(data)