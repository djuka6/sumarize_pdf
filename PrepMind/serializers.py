from rest_framework import serializers
from .models import SavedResponse


class ContentSerializer(serializers.Serializer):
    img_url = serializers.CharField()


class SavedResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedResponse
        fields = ["id", "question", "answer"]


class CheckAnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    answer = serializers.CharField(required=True)
