# Budget Requests

An internal tool for submitting and approving budget requests. Clients submit requests, Managers approve or reject them, and Admins see the organization's totals and clean up records. It is built on a Django + Inertia.js + React starter kit: Django owns routing, authentication, permissions and validation, and React only renders the props it receives.

**Walkthrough videos (Loom):**
- [Part 1](https://www.loom.com/share/9dd4131ca86241b4bf931d5556c888bb)
- [Part 2](https://www.loom.com/share/44f5d954c74a40b3a5314a99d5cf0e5d)

## Roles

| Role | Can do |
|---|---|
| **Client** | Submit a request; edit or withdraw it while it is pending; track the decision and the manager's note |
| **Manager** | See every pending request (oldest first); approve or reject it, with a note required for rejections; see the decision history |
| **Admin** | See totals by status (pending vs approved and the rest); browse and filter every request; permanently delete a request |

Every signed-in user has exactly one role. It is stored on `UserProfile`; users without a profile are Clients, and superusers are always Admins. Superusers change roles from **Users → Change role** in the admin console.

## Quick start

**Requirements:** Python 3.12+ with [uv](https://github.com/astral-sh/uv), and Node.js 20.19+.

```bash
# Backend (repository root)
uv run python starterkit/manage.py migrate
uv run python starterkit/manage.py seed_demo
uv run python starterkit/manage.py runserver

# Frontend (second terminal)
cd starterkit/frontend
npm install
npm run dev
```

Open **http://127.0.0.1:8000/admin/login/**. Do not open the Vite URL (`localhost:5173`): it serves assets only, and Django renders the pages.

**Without uv**, use a regular virtual environment (on macOS/Linux, use `.venv/bin/` instead of `.venv/Scripts/`):

```bash
python -m venv .venv
.venv/Scripts/python -m pip install "django>=6.0.1" "inertia-django>=1.2.0" "celery[redis]>=5.6.3" "django-celery-beat>=2.9.0"
.venv/Scripts/python starterkit/manage.py migrate
.venv/Scripts/python starterkit/manage.py seed_demo
.venv/Scripts/python starterkit/manage.py runserver
```

### Configuration

No environment variables are needed for local development. The defaults run in debug mode with SQLite at `starterkit/db.sqlite3`, and Redis is not required to use the budget workflow. The main variables are:

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_DEBUG` | `true` | Set to `false` in production. `seed_demo` only runs when it is `true`. |
| `DJANGO_SECRET_KEY` | development key | Required when `DJANGO_DEBUG=false` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated |
| `DJANGO_SQLITE_PATH` | `starterkit/db.sqlite3` | Database file |
| `VITE_DEV_SERVER_URL` | `http://localhost:5173` | Change it if port 5173 is taken, and set the same value for both processes |

The full list (security, login throttling, Redis and Celery) is in [docs/configuration.md](docs/configuration.md).

### Demo accounts

`seed_demo` creates these accounts and seven requests covering every status. It can be run again safely: it resets the passwords and skips requests that already exist. It refuses to run when `DEBUG` is off.

| Username | Password | Role |
|---|---|---|
| `client1` | `budget-demo-2026` | Client |
| `client2` | `budget-demo-2026` | Client |
| `manager1` | `budget-demo-2026` | Manager |
| `admin1` | `budget-demo-2026` | Admin |

To use the admin console (users, groups, role changes), also run `uv run python starterkit/manage.py createsuperuser`.

### Pages

| URL | Role | Page |
|---|---|---|
| `/workspace/` | All | Home after sign-in |
| `/budget/my-requests/` | Client | My requests, with Edit and Withdraw |
| `/budget/my-requests/new/` | Client | New request form |
| `/budget/review/?tab=pending` | Manager | Review queue (the `history` tab lists past decisions) |
| `/budget/review/<id>/` | Manager | Request details and decision form |
| `/budget/overview/` | Admin | Totals by status and every request |

A role that opens another role's page gets a 403 page. A Client who opens another Client's request gets a 404.

## Request lifecycle

```
            ┌── approve (Manager) ──► APPROVED
PENDING ────┼── reject + note (Manager) ──► REJECTED
            └── withdraw (owner) ──► WITHDRAWN

Admin can permanently delete a request in any status.
```

- Only **pending** requests can be edited, withdrawn or reviewed. Every decision is final.
- The amount must be positive, have at most two decimal places and be at most 9,999,999,999.99. Title and justification are required.

## Architecture

The code follows the layering in [CLAUDE.md](CLAUDE.md) and [docs/architecture.md](docs/architecture.md):

```
api/ (views)      parse the request → call ONE service → render Inertia or redirect
services/         business logic, transactions, page props; check policies first
domain/           models (own state + DB constraints) and policies (who may do what)
selectors/        every ORM read
dto/              frozen dataclasses for input and results
```

| App | Owns |
|---|---|
| `apps/users` | `UserProfile` and roles, role assignment, the workspace home |
| `apps/budgets` | `BudgetRequest`, the workflow services, and the Client, Manager and Admin pages |
| `apps/admin_panel` | The starter's admin console (users and groups), now showing each user's role |
| `shared/` | Request parsing, pagination and `ensure_allowed`, used by every app |

`budgets` reads roles only through `apps.users.selectors`, so the two apps never import each other's models or services.

**How one action flows:** a Manager rejects request 5.

1. React posts `{decision, note}` to the URL resolved from the route name `budget_review`.
2. The view builds a `ReviewInputDTO` and calls `review_request(actor=user, ...)`.
3. The service checks the policy and returns 403 for anyone who is not a Manager. It then opens a transaction, locks the row, checks that the request is still pending, validates the note and saves.
4. On success the view flashes a message and redirects to the queue, and Inertia swaps in the new props. On failure the service returns page props with the errors, and the view re-renders the detail page.

React never decides permissions. Each request carries `can: {edit, withdraw, review, delete}` flags computed by the same policies the services enforce, and buttons appear only when those flags are true.

## Decisions

- **Only Managers approve or reject; Admins do not.** This keeps duties separate: Managers decide, and Admins oversee and clean up. An Admin who also needs to review can be given a separate Manager account.
- **Withdraw is a status, delete is not.** A client's withdrawal keeps the record (`WITHDRAWN`) so the history stays complete. Permanent delete is a separate Admin-only action behind a confirmation dialog.
- **Decisions are final.** A rejection needs a note so the client knows why. Approved and rejected requests cannot be edited, withdrawn or reviewed again.
- **Rules are enforced in three places.** The UI hides what you cannot do, services raise `PermissionDenied` or return validation errors, and database `CheckConstraint`s keep invalid states out: a non-positive amount, an unknown status, a review date that doesn't match the status, or a rejection without a note.
- **403 vs 404.** A role that is not allowed on a page gets 403. That check runs before the database lookup, so it reveals nothing about which IDs exist. A Client asking for another Client's request gets 404, so request IDs cannot be probed.
- **Concurrency.** Edit, withdraw, review and delete run inside `transaction.atomic()` with `select_for_update()`. If two Managers act on the same request at once, the second sees "no longer pending" instead of overwriting the first decision.
- **Money is `Decimal`** (`DecimalField(12, 2)`) and travels to React as a string. It is never a float, so amounts and totals stay exact. Totals are computed in a single aggregate query.
- **Deleting users.** Deleting a Client deletes their requests (`CASCADE`). Deleting a Manager keeps their decisions, and the reviewer is shown as "Former user" (`SET_NULL`).

## Trade-offs and what I would do next

- **No audit trail.** Each request stores only its latest decision. A `BudgetRequestEvent` table would record who did what and when, and it would also let deleted requests leave a trace.
- **No notifications.** Clients see decisions when they open the app. Email on decision would go through a Celery task and an infrastructure adapter, enqueued with `transaction.on_commit`, as the starter's rules describe.
- **One currency, no budget limits.** Amounts are a single currency. There are no department budgets or approval thresholds, such as routing large requests to a second approver.
- **SQLite in development.** SQLite locks the whole database on write, so `select_for_update` is only fully exercised on PostgreSQL. The code is the same, and production should use PostgreSQL.
- **No search on the lists.** The lists are paginated and filtered by status or tab. Search can be added to the selectors without changing the pages' contract.
- **Roles are single-valued.** One role per user keeps the policies simple. Multiple roles would need a many-to-many table and a role switcher.

## Tests

```bash
uv run python starterkit/manage.py test --parallel 4   # backend

cd starterkit/frontend
npm run lint && npm test                               # frontend
```

The backend suite covers models and constraints, policies, selectors, validation, every workflow service (including a second review of a decided request, and edits after a decision), page props, views and route protection for each role, and the demo seed command. The frontend tests cover the pure helpers in `frontend/lib` (money, dates, routes, CSRF).

## Starter kit documentation

Setup details, the admin console, background tasks and deployment are documented in [docs/](docs/README.md): [Getting started](docs/getting-started.md), [Architecture](docs/architecture.md), [Permissions](docs/permissions.md), [Frontend](docs/frontend.md), [Testing](docs/testing.md), [Deployment](docs/deployment.md).
