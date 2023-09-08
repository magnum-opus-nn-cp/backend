import requests
import textract
from celery import shared_task

from press_release_nl.processor.models import Text

ML_HOST = "https://2b6a-176-59-106-6.ngrok-free.app/"


@shared_task
def load_text(pk: int):
    text = Text.objects.get(pk=pk)
    if not text.text:
        text.text = textract.process(text.file.path, encoding="unicode_escape").decode()
        text.save()
    re = requests.post(ML_HOST + "predict", json={"data": text.text})
    if re.status_code != 200:
        raise ValueError(re.text)
    text.score = re.json()
    text.save()
    return pk
