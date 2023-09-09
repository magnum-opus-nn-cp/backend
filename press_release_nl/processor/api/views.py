import requests
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, parsers, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from press_release_nl.processor.api.serializers import (
    EntrySerializer,
    ProcessedTextSerializer,
    TextSubmitSerializer,
)
from press_release_nl.processor.models import Entry, Text
from press_release_nl.processor.tasks import ML_HOST


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


@extend_schema_view(
    get=extend_schema(parameters=[OpenApiParameter(name="id", type=int)])
)
class RetrieveEntryApiView(generics.RetrieveAPIView):
    queryset = Entry.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = EntrySerializer
    lookup_field = "id"
    lookup_url_kwarg = "uuid"


class UpdateTextDescriptionApiView(generics.GenericAPIView):
    serializer_class = TextSubmitSerializer
    queryset = Text.objects.none()
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        # TODO: add get param for gen
        text = get_object_or_404(Text, id=self.kwargs["id"])
        if text.description:
            e = False
            if "bert" not in text.description:
                e = True
                text.description["bert"] = {}
                re = requests.post(ML_HOST + "bert/describe", json={"data": text.text})
                if re.status_code == 200:
                    text.description["bert"]["text"] = re.json()["text"]

            if "f" not in text.description:
                e = True
                text.description["f"] = {}
                re = requests.post(ML_HOST + "tfidf/describe", json={"data": text.text})
                if re.status_code == 200:
                    text.description["f"]["text"] = re.json()["text"]
            if e:
                text.save(update_fields=["description"])

        else:
            text.description = {"bert": {}, "f": {}}
            re = requests.post(ML_HOST + "bert/describe", json={"data": text.text})
            if re.status_code == 200:
                text.description["bert"]["text"] = re.json()["text"]
            re = requests.post(ML_HOST + "tfidf/describe", json={"data": text.text})
            if re.status_code == 200:
                text.description["f"]["text"] = re.json()["text"]
            text.save(update_fields=["description"])
        return Response(data=ProcessedTextSerializer().to_representation(instance=text))
