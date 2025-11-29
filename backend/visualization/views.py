from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from visualization.services.WorldMapService import get_world_map_data


class ForecastAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Vietnam",
            "predicted_cases": [100, 120, 150, 180]
        })

class AnalysisAPIView(APIView):
    def get(self, request):
        return Response({
            "country": "Huee",
            "predicted_cases": [100, 120, 150, 180]
        })
class VisualizationAPIView(APIView):
    def get(self, request):
        return Response({})


class WorldMapAPIView(APIView):
    def get(self, request):
        mode = request.query_params.get('mode', 'cases')  # ?mode=cases hoặc deaths
        if mode not in ['cases', 'deaths']:
            mode = 'cases'
        data = get_world_map_data(mode=mode)
        return Response(data)