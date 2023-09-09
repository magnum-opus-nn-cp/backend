from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from press_release_nl.processor.models import Entry, Text


class TextSubmitSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        file_fields = kwargs.pop("file_fields", None)
        super().__init__(*args, **kwargs)
        if file_fields:
            field_update_dict = {
                field: serializers.FileField(required=False, write_only=True)
                for field in file_fields
            }
            self.fields.update(**field_update_dict)

    id = serializers.UUIDField(source="entry.id", read_only=True)
    text = serializers.CharField(
        required=False, allow_null=True, max_length=25_000, write_only=True
    )
    file = serializers.FileField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Text
        fields = ["id", "text", "file"]
        extra_kwargs = {
            "id": {"read_only": True},
            "text": {"write_only": True},
            "file": {"write_only": True},
        }

    def validate(self, data):
        text = data["text"] if "text" in data else None
        files = [
            v
            for k, v in data.items()
            if isinstance(v, (TemporaryUploadedFile, InMemoryUploadedFile))
        ]
        if not (text or files):
            raise serializers.ValidationError("No data provided")

        if text and files:
            raise serializers.ValidationError("Should be one of text or files")

        return data

    def create(self, validated_data):
        text = validated_data["text"] if "text" in validated_data else None
        files = [
            v
            for k, v in validated_data.items()
            if isinstance(v, (TemporaryUploadedFile, InMemoryUploadedFile))
        ]

        entry = Entry.objects.create()

        if text:
            return Text.objects.create(entry=entry, text=text)
        else:
            t_files = [Text.objects.create(entry=entry, file=file) for file in files]
            return t_files[0]


class ProcessedTextSerializer(serializers.ModelSerializer):
    summary = serializers.CharField(source="summery")
    file_name = serializers.SerializerMethodField("get_file_name")

    @extend_schema_field(serializers.CharField)
    def get_file_name(self, obj):
        if not obj.file:
            return "Text"
        return obj.file.path.split("/")[-1]

    class Meta:
        model = Text
        fields = ["id", "file_name", "summary", "text", "score", "description"]


class EntrySerializer(serializers.ModelSerializer):
    texts = serializers.SerializerMethodField(method_name="get_texts")
    current = serializers.IntegerField(source="texts_done_count")
    total = serializers.IntegerField(source="texts_count")

    @extend_schema_field(ProcessedTextSerializer(many=True))
    def get_texts(self, obj: Entry):
        id = self.context["request"].query_params.get("id")
        q = obj.texts.all()
        if id:
            q = q.filter(id=id)
        return ProcessedTextSerializer(many=True).to_representation(q)

    class Meta:
        model = Entry
        fields = ["texts", "current", "total", "created"]
