from django.urls import path
from .views import ForecastAPIView, AnalysisAPIView

urlpatterns = [
    path('forecast/', ForecastAPIView.as_view(), name='forecast'),
    path('analysis/', AnalysisAPIView.as_view(), name='analysis'),
]
