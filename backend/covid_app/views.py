from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import os
from django.conf import settings
import logging

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


logger = logging.getLogger(__name__)


class WorldMapAPIView(APIView):
    def get(self, request):
        print("\n" + "*"*100)
        print("*** CODE MỚI NHẤT ĐÃ CHẠY - TOP10 SẼ HIỆN NGAY ***")
        print("*"*100 + "\n")

        mode = request.query_params.get('mode', 'cases').lower()

        parquet_path = os.path.join(settings.BASE_DIR, "core", "data", "cleaned_covid_data.parquet")
        try:
            df = pd.read_parquet(parquet_path)
        except Exception as e:
            return Response({"error": "Lỗi đọc file"}, status=500)

        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # Loại bỏ non-country
        exclude = ["World", "Europe", "European Union", "High income", "Low income", "Upper middle income", "Lower middle income", "Asia", "Africa", "North America", "South America", "Oceania", "International"]
        df = df[~df["location"].isin(exclude)]

        value_col = "total_deaths" if mode == "deaths" else "total_cases"
        map_title = "Tổng số ca tử vong COVID-19 theo quốc gia" if mode == "deaths" else "Tổng số ca nhiễm COVID-19 theo quốc gia"
        top_title = "Top 10 quốc gia có nhiều ca tử vong nhất" if mode == "deaths" else "Top 10 quốc gia có nhiều ca nhiễm nhất"

        df_map = df.groupby("location")[value_col].max().reset_index().dropna(subset=[value_col])

        df_top10 = df_map.sort_values(value_col, ascending=False).head(10)

        response_data = {
            "title": map_title,
            "locations": df_map["location"].tolist(),
            "values": df_map[value_col].fillna(0).astype(int).tolist(),
            "global_trends": {  # Global trend sum từ countries
                "dates": df.groupby("date")["total_cases"].sum().index.strftime("%Y-%m-%d").tolist(),
                "cases": df.groupby("date")["total_cases"].sum().fillna(0).astype(int).tolist(),
                "deaths": df.groupby("date")["total_deaths"].sum().fillna(0).astype(int).tolist(),
            },
            "top10": {
                "title": top_title,
                "countries": df_top10["location"].tolist(),
                "values": df_top10[value_col].fillna(0).astype(int).tolist()
            }
        }

        print("TOP 1:", df_top10.iloc[0]["location"] if not df_top10.empty else "RỖNG")
        return Response(response_data)
