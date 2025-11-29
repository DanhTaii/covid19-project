from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })