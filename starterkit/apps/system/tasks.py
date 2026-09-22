"""
Celery tasks: background entry points, the task-queue equivalent of views.

Each task calls exactly one service and holds no business logic. Give every
task an explicit name — schedules and callers refer to it by that string.
"""

from celery import shared_task

from apps.system.services import maintenance


@shared_task(name="system.clear_expired_sessions")
def clear_expired_sessions() -> int:
    return maintenance.clear_expired_sessions()
