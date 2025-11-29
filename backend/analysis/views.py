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

# Django views.py
class FullDataView(APIView):
    def get(self, request):
        df = pd.read_csv("owid-covid-data.csv")  # hoặc từ DB
        # preprocessing cơ bản: fillna(0) cho các cột số, v.v.
        return JsonResponse(df.to_dict(orient='records'), safe=False)