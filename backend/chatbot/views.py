from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from .services.engine import rag_chain  # Import chain từ engine của bạn
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

class ChatbotAPIView(APIView):
    def post(self, request):
        try:
            # Trong APIView, dữ liệu JSON gửi lên nằm trong request.data
            user_query = request.data.get('question')

            if not user_query:
                return Response({"error": "Bạn chưa nhập câu hỏi"}, status=status.HTTP_400_BAD_REQUEST)

            # Gọi "bộ não" RAG xử lý
            response = rag_chain.invoke(user_query)

            # Trả về kết quả dưới dạng JSON theo chuẩn DRF
            return Response({
                "answer": response
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": f"Lỗi hệ thống: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response({"message": "API Chatbot đang sẵn sàng. Hãy dùng phương thức POST để đặt câu hỏi!"})
