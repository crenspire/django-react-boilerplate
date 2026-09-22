# Testing

## Backend

```bash
uv run python starterkit/manage.py test                         # everything
uv run python starterkit/manage.py test apps.admin_panel.tests.test_policies
```

Tests live next to the code they cover:

| File | Covers |
|---|---|
| `apps/admin_panel/tests/test_policies.py` | Permission rules |
| `apps/admin_panel/tests/test_selectors.py` | Queries, counts, search, ordering |
| `apps/admin_panel/tests/test_*_services.py` | Business rules, validation, privilege checks, transactions |
| `apps/admin_panel/tests/test_views.py` | HTTP behaviour: redirects, 403/404/405, CSRF, flash messages, shared props |
| `apps/system/tests/` | Maintenance services, Celery tasks, beat schedule sanity |
| `main/tests/` | Route map and the `{% vite_assets %}` tag |

`apps/admin_panel/tests/factories.py` has helpers for common users:

```python
from apps.admin_panel.tests.factories import USER_PERMS, make_staff, make_superuser, make_user

manager = make_staff("manager", perms=USER_PERMS)   # staff with all user permissions
```

### What to test for a new feature

- **Selector** — the query returns the right rows (filters, ordering, counts).
- **Service** — the rules: allowed and denied actors, validation errors, edge cases.
- **Policy** — every branch, when the feature adds permissions.
- **View** — only when there is request parsing, redirects or status codes worth pinning down.

Inertia responses are JSON when the request has the `X-Inertia` header, which makes page props easy to assert:

```python
response = self.client.get("/admin/users/", HTTP_X_INERTIA="true", HTTP_X_INERTIA_VERSION="1.0")
props = response.json()["props"]
```

## Frontend

```bash
cd starterkit/frontend
npm run lint    # ESLint with React and hooks rules
npm test        # Vitest
```

Unit tests cover the pure helpers in `lib/` (`*.test.js`). Keep logic that is worth testing in `lib/` so components stay presentational.
