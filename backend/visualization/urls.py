from django.urls import path
from .views import ForecastAPIView, AnalysisAPIView, WorldMapAPIView, VisualizationAPIView

urlpatterns = [
    path('forecast/', ForecastAPIView.as_view(), name='forecast'),
    path('analysis/', AnalysisAPIView.as_view(), name='analysis'),
    path('visualization/', VisualizationAPIView.as_view(), name='visualization'),
    path('world-map/', WorldMapAPIView.as_view(), name='world-map'),
]
