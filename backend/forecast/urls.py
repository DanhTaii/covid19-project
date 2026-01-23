from django.urls import path
from .views import ForecastAPIView, ProphetAnalyticsView, ArimaAnalyticsView

urlpatterns = [
    path('forecast/', ForecastAPIView.as_view(), name='forecast'),

    path('prophet-predict/', ProphetAnalyticsView.as_view(), name='prophet_analytics'),

    path('arima-predict/', ArimaAnalyticsView.as_view(), name='arima_analytics'),

]