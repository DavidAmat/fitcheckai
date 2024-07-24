from rest_framework import serializers


class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    message = serializers.CharField(required=False)


class TextMessageSerializer(serializers.Serializer):
    thread_id = serializers.CharField(required=True)
    message = serializers.CharField(required=True)
