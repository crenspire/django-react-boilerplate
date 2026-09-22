# Background tasks

Long-running and scheduled work runs outside the request cycle with [Celery](https://docs.celeryq.dev/), using **Redis** as the message broker and result store. **Celery Beat** triggers periodic jobs, with schedules stored in the database by [django-celery-beat](https://django-celery-beat.readthedocs.io/) so they can be edited in `/django-admin/`.

```
Django (web) ──enqueue──► Redis ──► Celery worker ──► services ──► database
Celery Beat ──schedule──►   ▲
```

## Running locally

1. Start Redis. With Docker:

   ```bash
   docker compose up -d        # uses compose.yaml in the repository root
   ```

   Or install it natively (`brew install redis && brew services start redis` on macOS).

2. Start a worker and the scheduler (each in its own terminal, from `starterkit/`):

   ```bash
   uv run celery -A main worker -l info
   uv run celery -A main beat -l info
   ```

   Or start **everything** — web, Vite, worker and beat — with one command from the repository root:

   ```bash
   uvx honcho -f Procfile.dev start
   ```

3. Check the worker is reachable:

   ```bash
   cd starterkit && uv run celery -A main inspect ping
   ```

Don't want to run Redis at all while hacking on something unrelated? Set `CELERY_TASK_ALWAYS_EAGER=true` and tasks run inline in the web process.

## Included jobs

| Task | Schedule | What it does |
|---|---|---|
| `system.clear_expired_sessions` | Daily at 03:00 (`TIME_ZONE`) | Deletes expired database sessions. Django never removes them on its own. |
| `celery.backend_cleanup` | Daily at 04:00 | Added by Celery; purges expired task results. |

Default schedules live in `CELERY_BEAT_SCHEDULE` in `main/settings.py`. Beat copies them into the database when it starts; after that you can pause, reschedule or add jobs from **Django admin → Periodic tasks** without a deploy.

## Where code goes

Tasks are entry points, like views. They follow the same layering:

```
apps/<app>/tasks.py   ──► apps/<app>/services/   ──► selectors / policies
   (entry point)           (all the logic)
```

- A task calls **exactly one service** and contains no business logic.
- Give every task an explicit `name="<app>.<action>"`. Schedules and callers refer to it by that string, so renaming a function never breaks them.
- Pass **IDs, not model instances**, as arguments; load fresh data inside the service.
- Make tasks **idempotent**. `CELERY_TASK_ACKS_LATE` is on, so a task can run again if a worker dies mid-way.

Example, from `apps/system`:

```python
# apps/system/tasks.py
@shared_task(name="system.clear_expired_sessions")
def clear_expired_sessions() -> int:
    return maintenance.clear_expired_sessions()
```

## Queueing a task from a service

Services must not import task modules: tasks are entry points, so importing them would reverse the dependency direction. Queue work through a small infrastructure adapter in the same app instead:

```python
# apps/<app>/infrastructure/background.py
from celery import current_app
from django.db import transaction


def enqueue(task_name: str, **kwargs) -> None:
    """Queue a task once the current transaction commits (so the worker sees the data)."""
    transaction.on_commit(lambda: current_app.tasks[task_name].apply_async(kwargs=kwargs))
```

```python
# apps/<app>/services/reports.py
from apps.<app>.infrastructure import background

def request_export(*, actor, report_id: int) -> None:
    ensure_allowed(policies.can_export_reports(actor))
    background.enqueue("reports.build_export", report_id=report_id)
```

`transaction.on_commit` matters: without it the worker can pick up the task before the web request's transaction commits and find no data.

## Adding a periodic job

1. Write the service and its test.
2. Add a task in `apps/<app>/tasks.py` with an explicit name.
3. Add an entry to `CELERY_BEAT_SCHEDULE`:

   ```python
   "send-weekly-digest": {
       "task": "reports.send_weekly_digest",
       "schedule": crontab(day_of_week="mon", hour=8, minute=0),
   },
   ```

A test in `apps/system/tests/test_maintenance.py` checks that every schedule entry names a registered task, so a typo fails the build instead of silently never running.

## Testing tasks

Call the service directly for the logic, and use `.apply()` to run a task in-process — no broker or worker needed:

```python
result = clear_expired_sessions.apply()
self.assertEqual(result.get(), 1)
```

## Production

- Run **one or more workers** and **exactly one beat** process. Two beat processes would schedule every job twice.
- Point `REDIS_URL` (or `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND`) at a managed Redis.
- Set `DJANGO_CACHE_URL` to a Redis database (e.g. `/1`) so the login throttle is shared across web processes.
- Hard and soft time limits default to 5 and 4 minutes (`CELERY_TASK_TIME_LIMIT`, `CELERY_TASK_SOFT_TIME_LIMIT`).

See [Deployment](deployment.md) for process examples and [Configuration](configuration.md) for every variable.
