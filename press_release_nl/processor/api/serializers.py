from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
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
    class Meta:
        model = Text
        fields = ["text", "score"]


class EntrySerializer(serializers.ModelSerializer):
    texts = ProcessedTextSerializer(many=True)
    done = serializers.IntegerField(source="texts_done_count")
    count = serializers.IntegerField(source="texts_count")

    class Meta:
        model = Entry
        fields = ["texts", "done", "count", "created"]
