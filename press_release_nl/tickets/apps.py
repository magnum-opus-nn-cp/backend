from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "press_release_nl.tickets"

    def ready(self):
        try:
            import press_release_nl.tickets.signals  # noqa F401
        except ImportError:
            pass
