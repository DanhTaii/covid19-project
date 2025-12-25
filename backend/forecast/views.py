from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from .services.ProphetModel import predict_covid

class ProphetAnalyticsView(APIView):
    """
    Class xử lý dự báo COVID-19 (Phiên bản đã loại bỏ biến phong tỏa).
    """

    def get(self, request):
        # 1. Thu thập tham số từ URL
        location = request.query_params.get('location', 'Vietnam')
        start_date = request.query_params.get('start_date', '2022-01-01')

        try:
            # 2. Ép kiểu dữ liệu an toàn cho số ngày dự báo
            forecast_days = int(request.query_params.get('days', 30))

            # --- QUAN TRỌNG: KHÔNG LẤY VÀ KHÔNG GỬI STRINGENCY NỮA ---

            # 3. Thực thi dự báo thông qua Service (Đã bỏ tham số stringency_value)
            df_forecast = predict_covid(
                location=location,
                start_date_str=start_date,
                forecast_days=forecast_days
            )

            # 4. Chuyển đổi dữ liệu sang định dạng JSON
            # Chuyển cột ngày tháng (ds) sang chuỗi YYYY-MM-DD
            df_forecast['ds'] = df_forecast['ds'].dt.strftime('%Y-%m-%d')

            # Chuyển DataFrame thành danh sách để trả về
            records = df_forecast.to_dict(orient='records')

            # 5. Trả về kết quả
            return Response({
                "metadata": {
                    "country": location,
                    "start_point": start_date,
                    "days_predicted": forecast_days,
                    "model_type": "Univariate Prophet" # Ghi chú loại mô hình
                },
                "predictions": records
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Số ngày dự báo (days) phải là một số nguyên hợp lệ."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # In lỗi ra Terminal của Django để bạn dễ theo dõi
            print(f"❌ LỖI TẠI VIEW: {str(e)}")
            return Response({"error": f"Lỗi hệ thống: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })