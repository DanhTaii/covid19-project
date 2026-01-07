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

from django.http import JsonResponse
from .services.engine import rag_chain # Import chain từ engine của bạn

def ask_chatbot(request):
    if request.method == 'POST':
        user_query = request.POST.get('query')
        # Gọi chain đã xây dựng
        response = rag_chain.invoke(user_query)
        return JsonResponse({'answer': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)