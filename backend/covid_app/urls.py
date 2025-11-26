from django.urls import path
from .views import ForecastAPIView, AnalysisAPIView, OverviewAPIView, WorldMapAPIView

urlpatterns = [
    path('forecast/', ForecastAPIView.as_view(), name='forecast'),
    path('analysis/', AnalysisAPIView.as_view(), name='analysis'),
    path('visualization/', ForecastAPIView.as_view(), name='visualization'),
    path('overview/', OverviewAPIView.as_view(), name='overview'),
    path('world-map/', WorldMapAPIView.as_view(), name='world-map'),
]
