from django.db.models.signals import post_save
from django.dispatch import receiver

from press_release_nl.processor.models import Text
from press_release_nl.processor.tasks import load_text


@receiver(post_save, sender=Text)
def run_text_process(sender, instance: Text, created, **kwargs):
    if created:
        load_text.apply_async(kwargs={"pk": instance.pk}, countdown=1)
