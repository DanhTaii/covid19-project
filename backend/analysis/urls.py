from django.urls import path
from .views import ForecastAPIView,FactorCorrelationAPIView,MortalityRatioAPIView,WorldMapAPIView, CountryOverviewAPIView

urlpatterns = [
    path('forecast/', ForecastAPIView.as_view(), name='forecast'),
    path('world-map/', WorldMapAPIView.as_view(), name='world-map'),

    # 2. API lấy số liệu thống kê so sánh (Top/Bottom/Avg)
    # Frontend gọi: /api/analysis/mortality-ratio/
    path('mortality-ratio/', MortalityRatioAPIView.as_view(), name='mortality_ratio'),

    # Insight 4: Tương quan Yếu tố Rủi ro
    path('factor-correlation/', FactorCorrelationAPIView.as_view(), name='factor_correlation'),
    # Insight 1: Tổng quan quốc gia
    path('country-overview/', CountryOverviewAPIView.as_view(), name='country_overview'),
]