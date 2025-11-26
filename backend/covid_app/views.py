from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

@api_view(['GET'])
class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })

@api_view(['GET'])
class AnalysisAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Huee",
            "predicted_cases": [100, 120, 150, 180]
        })
@api_view(['GET'])
class VisualizationAPIView(APIView):
    def get(self, request):
        return Response({})

@api_view(['GET'])
class OverviewAPIView(APIView):
    def get(self, request):
        return Response({})