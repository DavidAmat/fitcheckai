from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UploadImageSerializer, TextMessageSerializer
from .chatbot_manager import ChatbotManager
import openai
import os

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


class PingView(APIView):
    def get(self, request):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)


class SubmitImageTextView(APIView):
    def post(self, request):
        serializer = UploadImageSerializer(data=request.data)
        if serializer.is_valid():
            image_file = request.FILES["image"]
            image_name = serializer.validated_data.get("image_name", None)
            occasion = serializer.validated_data.get("occasion", "General chat")
            message = serializer.validated_data.get("message", "")

            # Read the image file as binaries
            image_binary: bytes = image_file.read()

            # Create an instance of ChatbotManager
            manager = ChatbotManager(
                occasion=occasion,
            )

            # Submit the image with text using ChatbotManager
            result = manager.submit_image_with_text(
                image_binary=image_binary,
                message=message,
                image_name=image_name,
            )

            # Metadata for the response
            result["metadata"] = {
                "occasion": occasion,
                "image_name": image_name,
                "input_message": message,
            }

            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TextMessageView(APIView):
    def post(self, request):
        serializer = TextMessageSerializer(data=request.data)
        if serializer.is_valid():
            thread_id = serializer.validated_data["thread_id"]
            message = serializer.validated_data["message"]

            # Create an instance of ChatbotManager with the given thread and assistant IDs
            manager = ChatbotManager()

            # Submit the text message using ChatbotManager
            result = manager.submit_text(thread_id=thread_id, message=message)

            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
