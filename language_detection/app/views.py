import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import assemblyai as aai

from .serializers import AudioUploadSerializer, TranscribeAudioSerializer
from .config import ASSEMBLY_AI_API_KEY

logger = logging.getLogger("app")

if ASSEMBLY_AI_API_KEY:
    aai.settings.api_key = ASSEMBLY_AI_API_KEY


class AudioUploadView(APIView):
    serializer_class = AudioUploadSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        audio_file = serializer.validated_data["audio_file"]

        try:
            transcriber = aai.Transcriber()
            upload_url = transcriber.upload_file(data=audio_file)
            logger.info(f"File uploaded to {upload_url}")
            return Response(
                {"uploaded_audio_file_url": upload_url}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TranscribeAudioView(APIView):
    serializer_class = TranscribeAudioSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        audio_file = serializer.validated_data["audio_url"]
        threshold = serializer.validated_data["language_confidence_threshold"]

        try:
            transcriber = aai.Transcriber()
            config = aai.TranscriptionConfig(
                language_detection=True, language_confidence_threshold=threshold
            )

            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file, config=config)

            if transcript.error:
                logger.info("The Transcribe Audio Request is Complete with Error")
                return Response(
                    {"error": transcript.error}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                logger.info("The Transcribe Audio Request is Complete.")
                response = {
                    "transcript": transcript.text,
                    "language_code": transcript.json_response["language_code"],
                    "language_confidence": transcript.json_response[
                        "language_confidence"
                    ],
                }
                return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
