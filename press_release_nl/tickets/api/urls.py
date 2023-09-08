from django.urls import path

from press_release_nl.tickets.api.views import RetrieveTicketSerializer

urlpatterns = [
    path("<str:uuid>", RetrieveTicketSerializer.as_view(), name="ticket"),
]
