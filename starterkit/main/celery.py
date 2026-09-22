"""
Celery application.

Configuration comes from Django settings prefixed with CELERY_ (see
main/settings.py). Tasks are discovered from each installed app's `tasks`
module.

    celery -A main worker -l info     # run tasks
    celery -A main beat -l info       # schedule periodic tasks (run exactly one)
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

app = Celery("main")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
