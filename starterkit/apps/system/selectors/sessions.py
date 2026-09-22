from datetime import datetime

from django.contrib.sessions.models import Session
from django.db.models import QuerySet


def expired_sessions(*, now: datetime) -> QuerySet:
    return Session.objects.filter(expire_date__lt=now)
