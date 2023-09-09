from time import sleep

import requests
import textract
from celery import shared_task

from press_release_nl.processor.models import Entry, Text

ML_HOST = "http://192.168.107.95:8000/"
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
    try:
        entry = Entry.objects.get(pk=pk)
    except Entry.DoesNotExist:
        return
    if entry.texts.filter(text__isnull=True).exists():
        sleep(10)
    for text in entry.texts.all():
        re_bert = requests.post(ML_HOST + "bert/process", json={"data": text.text})
        re_tf = requests.post(ML_HOST + "tfidf/process", json={"data": text.text})
        if re_bert.status_code != 200:
            print(re_bert.status_code, "bert")
            continue
        if re_tf.status_code != 200:
            print(re_tf.status_code, "tf-idf")
            continue
        text.refresh_from_db()
        text.score = {
            "bert": re_bert.json(),
            "f": re_tf.json(),
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
