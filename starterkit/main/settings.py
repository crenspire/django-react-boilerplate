"""
Django settings for the starter kit.

Configuration comes from environment variables so the same settings file works
locally and in production. Defaults are tuned for local development; see
README.md for the variables production must set.
"""

import os
from pathlib import Path

from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return default if value is None else int(value)


def env_list(name: str, default: list[str]) -> list[str]:
    value = os.environ.get(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


# Core

DEBUG = env_bool("DJANGO_DEBUG", True)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is false.")
    SECRET_KEY = "django-insecure-local-development-only"

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"] if DEBUG else [])
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", [])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inertia',
    'django_celery_beat',
    'apps.admin_panel',
    'apps.system',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'inertia.middleware.InertiaMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'main.middleware.inertia_shared_props',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'admin_dashboard'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.csrf',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'vite': 'main.templatetags.vite',
            },
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get("DJANGO_SQLITE_PATH", BASE_DIR / 'db.sqlite3'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Security (production)

SESSION_COOKIE_SECURE = env_bool("DJANGO_SECURE_COOKIES", not DEBUG)
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = env_int("DJANGO_SECURE_HSTS_SECONDS", 0)
if env_bool("DJANGO_BEHIND_TLS_PROXY", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF uses Django's default cookie ("csrftoken") and header ("X-CSRFToken");
# frontend/app.jsx reads the cookie on every Inertia request. Avoid renaming the
# cookie to "XSRF-TOKEN": Laravel and Angular apps on the same host use that name
# and overwrite it with values Django rejects.


# Cache
#
# In-memory by default. Point DJANGO_CACHE_URL at Redis (e.g. redis://localhost:6379/1)
# so cached data — including login throttling counts — is shared by every worker.

DJANGO_CACHE_URL = os.environ.get("DJANGO_CACHE_URL", "")
if DJANGO_CACHE_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": DJANGO_CACHE_URL,
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


# Celery (see main/celery.py and docs/background-tasks.md)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_RESULT_EXPIRES = 60 * 60 * 24
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_SOFT_TIME_LIMIT = env_int("CELERY_TASK_SOFT_TIME_LIMIT", 4 * 60)
CELERY_TASK_TIME_LIMIT = env_int("CELERY_TASK_TIME_LIMIT", 5 * 60)
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Run tasks inline, without Redis or a worker (handy for quick local hacking).
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", False)
CELERY_TASK_EAGER_PROPAGATES = True

# Celery Beat keeps schedules in the database (django-celery-beat), editable at
# /django-admin/. Entries below are created or updated there each time beat starts.
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    "clear-expired-sessions": {
        "task": "system.clear_expired_sessions",
        "schedule": crontab(hour=3, minute=0),
    },
}


# Admin login throttling (see apps/admin_panel/infrastructure/attempt_counter.py)

ADMIN_LOGIN_MAX_ATTEMPTS = env_int("ADMIN_LOGIN_MAX_ATTEMPTS", 5)
ADMIN_LOGIN_LOCKOUT_SECONDS = env_int("ADMIN_LOGIN_LOCKOUT_SECONDS", 15 * 60)


# Static files and frontend

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# `static/` is Vite's build output and only exists after `npm run build`.
STATICFILES_DIRS = [path for path in (BASE_DIR / 'static', BASE_DIR / 'static_assets') if path.exists()]

VITE_DEV_MODE = env_bool("VITE_DEV_MODE", DEBUG)
VITE_DEV_SERVER_URL = os.environ.get("VITE_DEV_SERVER_URL", "http://localhost:5173")
VITE_MANIFEST_PATH = BASE_DIR / 'static' / 'manifest.json'

INERTIA_LAYOUT = 'base.html'
