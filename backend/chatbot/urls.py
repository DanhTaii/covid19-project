from django.urls import path
from .views import ChatbotAPIView

urlpatterns = [
    path('rag/', ChatbotAPIView.as_view(), name='chatbot'),
]