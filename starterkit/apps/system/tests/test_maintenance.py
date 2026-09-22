from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.utils import timezone

from apps.system.selectors.sessions import expired_sessions
from apps.system.services.maintenance import clear_expired_sessions
from apps.system.tasks import clear_expired_sessions as clear_expired_sessions_task
from main.celery import app as celery_app


def make_session(*, expires_in: timedelta) -> str:
    store = SessionStore()
    store["marker"] = True
    store.create()
    Session.objects.filter(session_key=store.session_key).update(expire_date=timezone.now() + expires_in)
    return store.session_key


class ExpiredSessionsSelectorTests(TestCase):
    def test_only_sessions_past_their_expiry_are_selected(self):
        expired = make_session(expires_in=timedelta(days=-1))
        make_session(expires_in=timedelta(days=1))

        keys = list(expired_sessions(now=timezone.now()).values_list("session_key", flat=True))

        self.assertEqual(keys, [expired])


class ClearExpiredSessionsServiceTests(TestCase):
    def test_deletes_expired_sessions_and_keeps_active_ones(self):
        make_session(expires_in=timedelta(days=-2))
        make_session(expires_in=timedelta(hours=-1))
        active = make_session(expires_in=timedelta(days=1))

        deleted = clear_expired_sessions()

        self.assertEqual(deleted, 2)
        self.assertEqual(list(Session.objects.values_list("session_key", flat=True)), [active])

    def test_nothing_to_delete(self):
        make_session(expires_in=timedelta(days=1))
        self.assertEqual(clear_expired_sessions(), 0)


class TaskTests(TestCase):
    def test_task_runs_the_service(self):
        make_session(expires_in=timedelta(days=-1))

        # apply() runs the task in-process: no broker or worker needed.
        result = clear_expired_sessions_task.apply()

        self.assertEqual(result.get(), 1)
        self.assertFalse(Session.objects.exists())

    def test_every_beat_schedule_entry_points_at_a_registered_task(self):
        registered = set(celery_app.tasks.keys())
        for name, entry in settings.CELERY_BEAT_SCHEDULE.items():
            with self.subTest(schedule=name):
                self.assertIn(entry["task"], registered)
