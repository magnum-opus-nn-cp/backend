import subprocess
from time import sleep

import requests
import textract
from celery import shared_task
from django.conf import settings

from press_release_nl.processor.models import Entry, Text
from press_release_nl.processor.services import create_highlighted_document
from press_release_nl.utils.celery import get_scheduled_tasks_name

ML_HOST = "http://192.168.107.95:8000/"
# ML_HOST = "https://dev2.akarpov.ru/"
ML_SUM_HOST = "https://dev.akarpov.ru/"


@shared_task
def load_text(pk: int):
    text = Text.objects.get(pk=pk)
    if not text.text:
        text.text = textract.process(
            text.file.path, encoding="unicode_escape", language="rus"
        ).decode()
        text.save()
    if not text.text:
        text.delete()
        return


@shared_task
def run_ml(pk: int, f=True):
    if get_scheduled_tasks_name().count("press_release_nl.processor.tasks.run_ml") >= 2:
        run_ml.apply_async(kwargs={"pk": pk}, countdown=10)
        return
    try:
        entry = Entry.objects.get(pk=pk)
    except Entry.DoesNotExist:
        return
    if entry.texts.filter(text__isnull=True).exists():
        run_ml.apply_async(kwargs={"pk": pk}, countdown=10)
        return
    for text in entry.texts.all():
        re_bert = requests.post(ML_HOST + "bert/process", json={"data": text.text})
        re_tf = requests.post(ML_HOST + "tfidf/process", json={"data": text.text})
        re_nearest = requests.post(
            ML_HOST + "nearest/nearest", json={"data": text.text}
        )
        if re_bert.status_code != 200:
            print(re_bert.status_code, "bert")
            continue
        if re_tf.status_code != 200:
            print(re_tf.status_code, "tf-idf")
            continue
        if re_nearest.status_code != 200:
            print(re_nearest.status_code, "nearest")
            continue

        text.refresh_from_db()
        text.score = {
            "bert": re_bert.json(),
            "f": re_tf.json(),
            "nearest": re_nearest.json(),
        }
        text.save(update_fields=["score"])
    return pk


@shared_task
def load_text_sum(pk: int):
    try:
        text = Text.objects.get(pk=pk)
    except Text.DoesNotExist:
        return
    if not text.text:
        sleep(3)
    text.refresh_from_db()
    re = requests.post(ML_SUM_HOST, json={"body": text.text})
    if re.status_code != 200:
        raise ValueError(re.status_code)
    data = re.json()
    text.refresh_from_db()
    text.summery = str(data)
    text.save(update_fields=["summery"])
    return pk


@shared_task
def run_create_highlighted_document(pk: int, var: str):
    text = Text.objects.get(pk=pk)
    if "file" in text.description[var]:
        return
    file_path = create_highlighted_document(pk, var)
    text.description[var]["file"] = file_path
    text.save()
    convert_to_pdf.apply_async(kwargs={"pk": pk, "var": var}, countdown=1)
    return pk


@shared_task
def convert_to_pdf(pk: int, var: str):
    text = Text.objects.get(pk=pk)
    if "pdf" in text.description[var]:
        return
    file_path = text.description[var]["file"]
    subprocess.run(
        "libreoffice --headless --convert-to pdf --outdir".split(" ")
        + [
            settings.MEDIA_ROOT + "/pdf",
            settings.MEDIA_ROOT.replace("/media", "") + file_path,
        ]
    )
    f_path = "/media/pdf/" + file_path.split("/")[-1].replace("docx", "pdf")
    text.description[var]["pdf"] = f_path
    text.save()
