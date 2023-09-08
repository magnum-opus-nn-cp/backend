from django.urls import include, path

app_name = "api"
urlpatterns = [
    path("ticket/", include("press_release_nl.tickets.api.urls")),
    path("process/", include("press_release_nl.processor.api.urls")),
]
