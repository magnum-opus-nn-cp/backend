from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "press_release_nl.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import press_release_nl.users.signals  # noqa F401
        except ImportError:
            pass
