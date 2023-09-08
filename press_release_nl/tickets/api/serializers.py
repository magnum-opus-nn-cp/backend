from rest_framework import serializers

from press_release_nl.tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    current = serializers.IntegerField()

    class Meta:
        model = Ticket
        fields = ["name", "current", "max", "next"]
