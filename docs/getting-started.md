# Getting started

## Requirements

- Python 3.12 or newer. [uv](https://github.com/astral-sh/uv) is recommended; the commands below use it.
- Node.js 20.19+ or 22.12+ (required by Vite 7).

## 1. Install and run the backend

From the repository root:

```bash
uv run python starterkit/manage.py migrate
uv run python starterkit/manage.py createsuperuser
uv run python starterkit/manage.py runserver
```

`uv run` creates the virtual environment and installs the Python dependencies on first use. The development database is SQLite at `starterkit/db.sqlite3`.

## 2. Run the frontend dev server

In a second terminal:

```bash
cd starterkit/frontend
npm install
npm run dev
```

Django renders the HTML and loads JavaScript from the Vite dev server (`http://localhost:5173`) with hot module replacement. Keep both processes running.

> **Port already in use?** Start Vite on another port and tell Django about it with the same variable:
>
> ```bash
> VITE_DEV_SERVER_URL=http://localhost:5180 npm run dev
> VITE_DEV_SERVER_URL=http://localhost:5180 uv run python starterkit/manage.py runserver
> ```

## 3. Background tasks (optional)

Scheduled jobs and anything queued with Celery need Redis, a worker and the beat scheduler:

```bash
docker compose up -d                           # Redis on localhost:6379
cd starterkit
uv run celery -A main worker -l info           # third terminal
uv run celery -A main beat -l info             # fourth terminal
```

Or run web, Vite, worker and beat together from the repository root with `uvx honcho -f Procfile.dev start`. The site works without them; only background jobs wait. See [Background tasks](background-tasks.md).

## 4. Open the app

| URL | What |
|---|---|
| http://127.0.0.1:8000/ | Landing page |
| http://127.0.0.1:8000/admin/login/ | Admin sign in |
| http://127.0.0.1:8000/admin/ | Dashboard |
| http://127.0.0.1:8000/admin/users/ | Users |
| http://127.0.0.1:8000/admin/groups/ | Groups |
| http://127.0.0.1:8000/django-admin/ | Classic Django admin |

Sign in with the superuser you created. Staff users need model permissions (or group membership) to see Users and Groups — see [Permissions](permissions.md).

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| ⌘K / Ctrl+K | Open the command palette |
| ⌘B / Ctrl+B | Collapse or expand the sidebar |

## Project layout

```
.
├── docs/                         # This documentation
├── pyproject.toml / uv.lock      # Python dependencies
├── compose.yaml                  # Redis for local development
├── Procfile.dev                  # web + vite + worker + beat via honcho
└── starterkit/
    ├── manage.py
    ├── main/                     # Django project
    │   ├── settings.py           #   environment-driven settings
    │   ├── urls.py               #   all URL routes
    │   ├── routes.py             #   route names exposed to React
    │   ├── middleware.py         #   shared Inertia props (auth, flash, routes, nav)
    │   ├── celery.py             #   Celery app
    │   └── templatetags/vite.py  #   {% vite_assets %}
    ├── apps/admin_panel/         # The admin console (see Architecture)
    ├── apps/system/              # Maintenance services and Celery tasks
    ├── templates/base.html       # Inertia root template
    ├── static_assets/            # Static files served at /static/
    └── frontend/                 # React app
        ├── app.jsx               #   Inertia entry point
        ├── main.css              #   Tailwind + shadcn/ui theme tokens
        ├── Pages/                #   Inertia pages (Admin/*, Auth/*, Home.jsx)
        ├── Layouts/              #   AdminLayout, AuthLayout
        ├── Components/ui/        #   shadcn/ui components
        ├── Components/admin/     #   app-specific components
        ├── composables/          #   React hooks
        └── lib/                  #   pure helpers
```

## Next steps

- Read [Architecture](architecture.md) before adding features — it walks through adding a page end to end.
- Change the look in [Frontend → Theming](frontend.md#theming).
- Ready to ship? Follow [Deployment](deployment.md).
