from django.shortcuts import render
from rest_framework import status
import pandas as pd
import os
from django.conf import settings

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from analysis.services.SummaryService import SummaryService
from analysis.services.FactorCorrelationService import FactorCorrelationService
from analysis.services.MortalityRatioService import MortalityRatioService
from analysis.services.TransmissionRateService import TransmissionRateService

class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })

# Django views.py
class FullDataView(APIView):
    def get(self, request):
        df = pd.read_csv("owid-covid-data.csv")  # hoặc từ DB
        # preprocessing cơ bản: fillna(0) cho các cột số, v.v.
        return Response(df.to_dict(orient='records'), safe=False)


class CountryOverviewAPIView(APIView):
    """
    [Insight 1]
    API trả về tổng quan cho 1 quốc gia:
    - Tổng ca nhiễm
    - Tổng ca tử vong
    - Tỉ lệ tử vong (%)
    - Tỉ lệ tiêm chủng (%)
    Endpoint: /api/analysis/country-overview/?location=Vietnam
    """

    def get(self, request):
        # 1. Lấy location
        location = request.query_params.get("location")

        # 2. Validate
        if not location:
            return Response(
                {
                    "message": "Chưa chọn quốc gia",
                    "data": None
                },
                status=status.HTTP_200_OK
            )

        # 3. Gọi service
        try:
            service = SummaryService()
            data = service.get_country_summary(location)

            # Nếu service trả rỗng
            if not data:
                return Response(
                    {
                        "message": f"Không có dữ liệu cho {location}",
                        "data": None
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {
                    "message": "OK",
                    "data": data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Lỗi CountryOverviewAPIView: {e}")
            return Response(
                {
                    "message": "Lỗi xử lý dữ liệu",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorldMapAPIView(APIView):
    """
    [Insight 3 - Map]
    API cung cấp dữ liệu cho Bản đồ Choropleth (Tỷ lệ tử vong/Triệu dân).
    Endpoint: /api/analysis/world-map/?mode=deaths
    """

    def get(self, request):
        mode = request.query_params.get('mode', 'deaths')

        try:
            service = MortalityRatioService()

            if mode == 'deaths':
                # Lấy dữ liệu tỷ lệ tử vong cho bản đồ
                data = service.get_choropleth_data()
            else:
                # Mở rộng cho các mode khác sau này (ví dụ: cases)
                data = []

            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MortalityRatioAPIView(APIView):
    """
    [Insight 3]
    API này bây giờ trả về cả:
    1. map_data: Dữ liệu để vẽ bản đồ (tô màu quốc gia được chọn).
    2. statistic: Số liệu cụ thể của quốc gia đó để hiện lên thẻ Metric.
    Endpoint: /api/analysis/mortality-ratio/?location=Vietnam
    """

    def get(self, request):
        try:
            # 1. Lấy tham số location từ URL (Frontend gửi lên)
            location = request.query_params.get('location', 'All Countries')

            service = MortalityRatioService()

            # 2. Gọi 2 hàm mới từ Service
            map_data = service.get_choropleth_data(location=location)
            statistic = service.get_selected_country_stat(location=location)

            # 3. Trả về format JSON khớp với Frontend mới
            return Response({
                'map_data': map_data,
                'statistic': statistic
            })

        except Exception as e:
            print(f"Lỗi tại MortalityRatioAPIView: {e}")  # In lỗi ra terminal để debug
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FactorCorrelationAPIView(APIView):
        def get(self, request):
            try:
                service = FactorCorrelationService()
                correlation_matrix = service.get_correlation_matrix()
                scatter_data = service.get_scatter_data()

                return Response({
                    'correlation_matrix': correlation_matrix,
                    'scatter_data': scatter_data
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TransmissionRateAPIView(APIView):
    def get(self, request):
        try:
            location = request.query_params.get('location')
            if not location:
                return Response({"error": "Location is required"}, status=status.HTTP_400_BAD_REQUEST)

            service = TransmissionRateService()
            data = service.get_transmission_data(location)

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Lỗi tại TransmissionRateAPIView: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)