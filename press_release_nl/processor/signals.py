import openpyxl
from django.db.models.signals import post_save
from django.dispatch import receiver

from press_release_nl.processor.models import Text
from press_release_nl.processor.tasks import load_text, load_text_sum


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
        load_text.apply_async(kwargs={"pk": instance.pk}, countdown=2)
        load_text_sum.apply_async(kwargs={"pk": instance.pk}, countdown=4)
