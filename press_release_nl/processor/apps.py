from django.apps import AppConfig


class ProcessorConfig(AppConfig):
    name = "press_release_nl.processor"

    def ready(self):
        import press_release_nl.processor.signals  # noqa
