from django.urls import path

from press_release_nl.processor.api.views import (
    RetrieveEntryApiView,
    SubmitTextsApiView,
    UpdateTextDescriptionApiView,
)

app_name = "processor"

urlpatterns = [
    path("", SubmitTextsApiView.as_view()),
    path("<str:uuid>", RetrieveEntryApiView.as_view()),
    path("describe/<int:id>", UpdateTextDescriptionApiView.as_view()),
]
