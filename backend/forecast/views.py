import numpy as np
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
        # 1. Lấy các tham số từ Query Parameters
        location = request.query_params.get('location', 'Vietnam')
        start_date = request.query_params.get('start_date', '2022-01-01')

        # Lấy chỉ số phong tỏa từ slider trên giao diện (ví dụ: 0 đến 100)
        user_stringency = request.query_params.get('stringency_level', None)

        try:
            forecast_days = int(request.query_params.get('days', 30))

            # Chuyển đổi user_stringency sang float nếu có truyền vào
            if user_stringency is not None:
                user_stringency = float(user_stringency)

            # 2. Gọi service với tham số user_stringency mới
            df_forecast, mape_score, mae_score,actual_stringency = predict_covid(
                location=location,
                start_date_str=start_date,
                forecast_days=forecast_days,
                user_stringency=user_stringency  # Truyền mức phong tỏa giả định vào
            )

            # 3. Định dạng dữ liệu trước khi gửi về Frontend
            # Chuyển cột ngày tháng sang chuỗi YYYY-MM-DD
            df_forecast['ds'] = df_forecast['ds'].dt.strftime('%Y-%m-%d')

            # Xử lý các giá trị NaN/None để tránh lỗi JSON
            df_forecast = df_forecast.replace({np.nan: None})

            # Chuyển DataFrame thành danh sách các Dictionary (records)
            # Lúc này records sẽ có các key: ds, y_actual, yhat_baseline, yhat_scenario
            records = df_forecast.to_dict(orient='records')

            return Response({
                "metadata": {
                    "country": location,
                    "mape": mape_score,
                    "mae": mae_score,
                    "applied_stringency": user_stringency if user_stringency is not None else "Actual",
                    "actual_stringency": actual_stringency,
                    "model_type": "Prophet Multivariate"
                },
                "predictions": records
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                "error": str(e),
                "detail": "Vui lòng kiểm tra lại tên quốc gia hoặc định dạng ngày tháng."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })