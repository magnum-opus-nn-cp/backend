from time import sleep

import requests
import textract
from celery import shared_task

from press_release_nl.processor.models import Text

ML_HOST = "https://2b6a-176-59-106-6.ngrok-free.app/"
ML_SUM_HOST = "https://dev.akarpov.ru/"


@shared_task
def load_text(pk: int):
    text = Text.objects.get(pk=pk)
    if not text.text:
        text.text = textract.process(
            text.file.path, encoding="unicode_escape", language="rus"
        ).decode()
        text.save()
    re = requests.post(ML_HOST + "predict", json={"data": text.text})
    if re.status_code != 200:
        raise ValueError(re.text)
    text.score = re.json()
    text.save()
    return pk


@shared_task
def load_text_sum(pk: int):
    text = Text.objects.get(pk=pk)
    if not text.text:
        sleep(3)
    text.refresh_from_db()
    re = requests.post(ML_SUM_HOST, json={"body": text.text})
    if re.status_code != 200:
        raise ValueError(re.text)
    data = re.json()
    text.summery = str(data)
    text.save()
    return pk
