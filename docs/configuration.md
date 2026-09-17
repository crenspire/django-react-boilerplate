# Configuration

All settings come from environment variables read in [`main/settings.py`](../starterkit/main/settings.py). Defaults are tuned for local development, so nothing needs to be set to run the app locally.

## Core

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_DEBUG` | `true` | Set to `false` in production. |
| `DJANGO_SECRET_KEY` | development-only key | **Required** when `DJANGO_DEBUG=false`; startup fails without it. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` in debug, empty otherwise | Comma-separated host names. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | – | Comma-separated origins, e.g. `https://admin.example.com`. |
| `DJANGO_SQLITE_PATH` | `starterkit/db.sqlite3` | Path of the SQLite database. |

## Security

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_SECURE_COOKIES` | `true` when not debug | Marks session and CSRF cookies `Secure`. |
| `DJANGO_SECURE_SSL_REDIRECT` | `false` | Redirect HTTP to HTTPS in Django (often done by the proxy instead). |
| `DJANGO_SECURE_HSTS_SECONDS` | `0` | Enable HSTS once HTTPS works everywhere. |
| `DJANGO_BEHIND_TLS_PROXY` | `false` | Trust `X-Forwarded-Proto` from your load balancer. |

## Admin sign-in throttling

| Variable | Default | Notes |
|---|---|---|
| `ADMIN_LOGIN_MAX_ATTEMPTS` | `5` | Failures allowed per username + client before blocking (a client is blocked after 4× this across usernames). |
| `ADMIN_LOGIN_LOCKOUT_SECONDS` | `900` | Window for counting failures. |

Throttling uses Django's cache. The default in-memory cache is per process — configure a shared cache (Redis, Memcached or the database cache) when running several workers.

## Frontend assets

| Variable | Default | Notes |
|---|---|---|
| `VITE_DEV_MODE` | same as `DJANGO_DEBUG` | `true` loads scripts from the Vite dev server; `false` uses the built manifest. |
| `VITE_DEV_SERVER_URL` | `http://localhost:5173` | Read by **both** Django and `vite.config.js`, so set it for both processes. |

To preview a production build locally:

```bash
cd starterkit/frontend && npm run build && cd ../..
VITE_DEV_MODE=false uv run python starterkit/manage.py runserver
```

## Using another database

`DATABASES` is SQLite by default. For PostgreSQL, install a driver (`uv add "psycopg[binary]"`) and replace the `DATABASES` block in `settings.py`, reading credentials from environment variables in the same style.
