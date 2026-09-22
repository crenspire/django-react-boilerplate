# Deployment

The app deploys as a Django web service plus Celery worker and beat processes, all from the same code, with Redis alongside. There is no separate frontend server in production: Vite builds static files that Django (or your web server) serves.

## 1. Build the frontend

```bash
cd starterkit/frontend
npm ci
npm run build
```

This writes hashed assets and `manifest.json` to `starterkit/static/`. The `{% vite_assets %}` tag in `templates/base.html` reads the manifest to emit the right `<script>` and `<link>` tags.

## 2. Configure the environment

At minimum:

```bash
export DJANGO_DEBUG=false
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_ALLOWED_HOSTS=admin.example.com
export DJANGO_CSRF_TRUSTED_ORIGINS=https://admin.example.com
```

See [Configuration](configuration.md) for the rest.

## 3. Prepare Django

```bash
uv run python starterkit/manage.py migrate
uv run python starterkit/manage.py collectstatic --noinput
uv run python starterkit/manage.py check --deploy
```

`collectstatic` copies everything into `starterkit/staticfiles/` (`STATIC_ROOT`).

## 4. Run it

Use a production server rather than `runserver`, for example:

```bash
uv add gunicorn
cd starterkit && uv run gunicorn main.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Run the background processes alongside the web server (see [Background tasks](background-tasks.md)):

```bash
cd starterkit && uv run celery -A main worker -l info --concurrency 4
cd starterkit && uv run celery -A main beat -l info      # exactly one instance
```

Serve `STATIC_ROOT` at `/static/` with one of:

- your reverse proxy (nginx, Caddy) pointing at `starterkit/staticfiles/`
- a CDN or object storage
- [WhiteNoise](https://whitenoise.readthedocs.io/) inside Django

## Checklist

- [ ] `DJANGO_DEBUG=false` and a strong `DJANGO_SECRET_KEY`
- [ ] `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` set
- [ ] HTTPS enabled; `DJANGO_BEHIND_TLS_PROXY=true` if TLS ends at a proxy
- [ ] `DJANGO_SECURE_HSTS_SECONDS` raised once HTTPS is stable
- [ ] Redis provisioned; `REDIS_URL` set for Celery and `DJANGO_CACHE_URL` for a shared cache
- [ ] Celery worker(s) and exactly **one** beat process running
- [ ] A production database (PostgreSQL recommended) and backups
- [ ] `npm run build` and `collectstatic` run on every deploy
- [ ] `manage.py check --deploy` passes

## Can I host it on GitHub Pages?

No — GitHub Pages only serves static files, and this app needs Django running. Use a platform that runs Python (Render, Fly.io, Railway, a VPS, …). GitHub Pages is still a good fit for **documentation** if you want a docs website.
