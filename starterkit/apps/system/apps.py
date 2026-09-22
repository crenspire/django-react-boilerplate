from django.apps import AppConfig


class SystemConfig(AppConfig):
    """Project-wide maintenance and background jobs."""

    name = "apps.system"
    verbose_name = "System"
