import openpyxl
from django.db.models.signals import post_save
from django.dispatch import receiver

from press_release_nl.processor.models import Entry, Text
from press_release_nl.processor.tasks import (
    load_text,
    load_text_sum,
    run_create_highlighted_document,
    run_ml,
)


@receiver(post_save, sender=Text)
def run_text_process(sender, instance: Text, created, **kwargs):
    if created:
        if instance.file and instance.file.path.endswith("xlsx"):
            wb_obj = openpyxl.load_workbook(instance.file.path)
            sheet = wb_obj.worksheets[0]
            for column in sheet.iter_cols():
                column_name = column[0].value
                if column_name == "pr_txt":
                    for text in column:
                        text = text.value
                        if text and text != "pr_txt":
                            Text.objects.create(entry=instance.entry, text=text)
                    instance.delete()
                    return
        load_text.apply_async(kwargs={"pk": instance.pk}, countdown=1)
        load_text_sum.apply_async(kwargs={"pk": instance.pk}, countdown=4)
    if instance.description:
        for k, v in instance.description.items():
            if "file" not in v:
                run_create_highlighted_document.apply_async(
                    kwargs={"pk": instance.pk, "var": k}, countdown=1
                )


@receiver(post_save, sender=Entry)
def run_entry_ml(sender, instance: Entry, created, **kwargs):
    if created:
        run_ml.apply_async(kwargs={"pk": instance.pk}, countdown=4)
