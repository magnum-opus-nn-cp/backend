import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Entry(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.id

    @property
    def texts_done_count(self):
        return len(self.texts.filter(score__isnull=False, summery__isnull=False))

    @property
    def texts_count(self):
        return len(self.texts.all())


class Text(models.Model):
    entry = models.ForeignKey("Entry", related_name="texts", on_delete=models.CASCADE)
    summery = models.TextField(max_length=2000, blank=True, null=True)
    file = models.FileField(blank=True, null=True, upload_to="uploads/")
    text = models.TextField(blank=True, null=True, max_length=25_000)
    score = models.JSONField(null=True)
    description = models.JSONField(null=True)

    def __str__(self):
        return f"{self.text}"[:200]
