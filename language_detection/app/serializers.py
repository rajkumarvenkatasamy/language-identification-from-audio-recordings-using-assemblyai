from rest_framework import serializers


class AudioUploadSerializer(serializers.Serializer):
    audio_file = serializers.FileField()


class TranscribeAudioSerializer(serializers.Serializer):
    audio_url = serializers.CharField()
    language_confidence_threshold = serializers.FloatField()
