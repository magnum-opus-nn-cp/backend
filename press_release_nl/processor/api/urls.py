from django.urls import path

from press_release_nl.processor.api.views import (
    RetrieveEntryApiView,
    SubmitTextsApiView,
)

app_name = "processor"

urlpatterns = [
    path("", SubmitTextsApiView.as_view()),
    path("<str:uuid>", RetrieveEntryApiView.as_view()),
]
