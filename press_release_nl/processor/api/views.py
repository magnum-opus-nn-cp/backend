from rest_framework import generics, parsers, permissions, status
from rest_framework.response import Response

from press_release_nl.processor.api.serializers import (
    EntrySerializer,
    TextSubmitSerializer,
)
from press_release_nl.processor.models import Entry, Text


class SubmitTextsApiView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = TextSubmitSerializer
    queryset = Text.objects.none()
    parser_classes = [parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser]

    def create(self, request, *args, **kwargs):
        file_fields = list(request.FILES.keys())
        serializer = self.get_serializer(data=request.data, file_fields=file_fields)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class RetrieveEntryApiView(generics.RetrieveAPIView):
    queryset = Entry.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EntrySerializer
    lookup_field = "id"
    lookup_url_kwarg = "uuid"
