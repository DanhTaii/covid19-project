from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from .services.ProphetModel import predict_covid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from .services.ProphetModel import predict_covid


class ProphetAnalyticsView(APIView):
    def get(self, request):
        location = request.query_params.get('location', 'Vietnam')
        start_date = request.query_params.get('start_date', '2022-01-01')

        try:
            forecast_days = int(request.query_params.get('days', 30))

            # Gọi service lấy cả dataframe và mape
            df_forecast, mape_score = predict_covid(
                location=location,
                start_date_str=start_date,
                forecast_days=forecast_days
            )

            # Format dữ liệu cho JSON
            df_forecast['ds'] = df_forecast['ds'].dt.strftime('%Y-%m-%d')
            df_forecast = df_forecast.where(pd.notnull(df_forecast), None)
            records = df_forecast.to_dict(orient='records')

            return Response({
                "metadata": {
                    "country": location,
                    "mape": mape_score,
                    "model_type": "Prophet Optimized (0.1)"
                },
                "predictions": records
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })