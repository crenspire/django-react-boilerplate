import logging
from datetime import datetime

from django.utils import timezone

from apps.system.selectors.sessions import expired_sessions

logger = logging.getLogger(__name__)


def clear_expired_sessions(*, now: datetime | None = None) -> int:
    """
    Delete database sessions that have expired and return how many were removed.

    Django never deletes expired sessions on its own, so without this the session
    table grows forever. Runs nightly via Celery Beat (see CELERY_BEAT_SCHEDULE).
    """

    deleted, _ = expired_sessions(now=now or timezone.now()).delete()
    logger.info("Deleted %d expired sessions", deleted)
    return deleted
