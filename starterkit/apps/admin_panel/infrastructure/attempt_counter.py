"""
Cache-backed counter for throttling repeated attempts (e.g. failed logins).

This is the only place the admin panel touches the cache. With the default
LocMemCache counts are per process; configure a shared cache (Redis,
Memcached, database) in production so limits apply across workers.
"""

from django.core.cache import cache


def get_count(key: str) -> int:
    return cache.get(key, 0)


def increment(key: str, *, window_seconds: int) -> int:
    # add() is a no-op when the key exists, so the window starts at the first attempt.
    cache.add(key, 0, timeout=window_seconds)
    try:
        return cache.incr(key)
    except ValueError:
        # The key expired between add() and incr().
        cache.set(key, 1, timeout=window_seconds)
        return 1


def reset(key: str) -> None:
    cache.delete(key)
