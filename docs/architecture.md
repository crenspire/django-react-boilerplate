# Architecture

Django is the single source of truth: it owns routing, authentication, permissions, validation and data. React renders what Django sends and never decides who may do what. Inertia connects the two — every page is a normal Django view that returns a React component name plus props.

## Layers

Dependencies flow in one direction:

```
api (views)    ─┐
tasks (Celery) ─┴─► services ──► selectors / domain (policies) ──► infrastructure
```

| Layer | Location | Responsibility | Must not |
|---|---|---|---|
| **Views** | `apps/*/api/` | Parse the request into a DTO, call **one** service, return an Inertia response or redirect | Query the ORM, check permissions, contain business rules |
| **Tasks** | `apps/*/tasks.py` | Celery entry points: call **one** service with IDs/primitive arguments | Contain business logic or be imported by services |
| **Services** | `apps/*/services/` | Business logic, permission checks, transactions, building page props | Return `HttpResponse` objects |
| **Selectors** | `apps/*/selectors/` | Every ORM query; return QuerySets or model instances | Contain business rules |
| **Domain** | `apps/*/domain/` | Permission policies (pure functions of users) | Touch cache, HTTP or external services |
| **DTOs** | `apps/*/dto/` | Frozen dataclasses for inputs and results | Hold behaviour |
| **Infrastructure** | `apps/*/infrastructure/` | Adapters for cache, email, payments, … | Be imported by views or models |

Services receive the acting user (`actor`), not the request. The only exceptions are login and logout, which need Django's session APIs.

The full rule set used by contributors and AI assistants lives in [`CLAUDE.md`](../CLAUDE.md).

## Request lifecycle

Taking `GET /admin/users/?search=olivia` as an example:

1. **URL** — `main/urls.py` routes to `apps.admin_panel.api.user_views.user_list`.
2. **Middleware** — `main/middleware.py` shares lazy props with every page: `auth`, `flash` (Django messages), `routes` and `admin_nav`.
3. **View** — parses query parameters into a `ListQueryDTO` and calls one service:

   ```python
   @require_GET
   @login_required
   def user_list(request):
       props = user_services.get_user_list_page(actor=request.user, query=parse_list_query(request))
       return render(request, "Admin/Users/Index", props)
   ```

4. **Service** — checks the policy (raising `PermissionDenied` → 403), validates ordering, paginates the selector's QuerySet and returns props.
5. **Inertia** — the first visit returns HTML (`templates/base.html`) with the page JSON; later visits return JSON only and React swaps the page.
6. **React** — `frontend/Pages/Admin/Users/Index.jsx` renders the props inside `AdminLayout`.

Mutations work the same way. A failed mutation returns `page_props` to re-render the form with errors; a successful one adds a Django message and redirects, and the message appears as a toast.

## Adding a feature

This walkthrough adds a read-only **Permissions** page to the admin. The same steps apply to any page.

### 1. Selector — the query

```python
# apps/admin_panel/selectors/permissions.py
from django.contrib.auth.models import Permission
from django.db.models import Q, QuerySet


def permission_list(*, search: str = "") -> QuerySet:
    qs = Permission.objects.select_related("content_type").order_by("content_type__app_label", "codename")
    if search.strip():
        qs = qs.filter(Q(codename__icontains=search) | Q(name__icontains=search))
    return qs
```

### 2. Policy — who may see it

```python
# apps/admin_panel/domain/policies.py
def can_view_permissions(user: UserLike) -> bool:
    return _has_admin_perm(user, "auth.view_permission")
```

### 3. Service — logic and page props

```python
# apps/admin_panel/services/permissions.py
from apps.admin_panel.domain import policies
from apps.admin_panel.dto.common import ListQueryDTO
from apps.admin_panel.selectors.permissions import permission_list
from apps.admin_panel.services.common import ensure_allowed, paginate


def get_permission_list_page(*, actor, query: ListQueryDTO) -> dict:
    ensure_allowed(policies.can_view_permissions(actor))
    page, pagination = paginate(permission_list(search=query.search), page=query.page, page_size=query.page_size)
    return {
        "permissions": [
            {"id": p.pk, "name": p.name, "codename": f"{p.content_type.app_label}.{p.codename}"}
            for p in page
        ],
        "pagination": pagination,
        "filters": {"search": query.search, "order_by": ""},
    }
```

### 4. View and URL

```python
# apps/admin_panel/api/permission_views.py
@require_GET
@login_required
def permission_list(request):
    props = permission_services.get_permission_list_page(actor=request.user, query=parse_list_query(request))
    return render(request, "Admin/Permissions/Index", props)
```

```python
# main/urls.py
path("admin/permissions/", permission_list, name="admin_permissions"),
```

### 5. Expose the route and add it to the sidebar

```python
# main/routes.py — React can only resolve names listed here
EXPOSED_ROUTE_NAMES = (..., "admin_permissions")
```

```python
# apps/admin_panel/services/navigation.py
if policies.can_view_permissions(actor):
    items.append({"section": "Management", "label": "Permissions", "icon": "permissions", "route": "admin_permissions"})
```

```jsx
// frontend/Layouts/AdminLayout.jsx
import { KeyRound } from "lucide-react"
const NAV_ICONS = { ..., permissions: KeyRound }
```

### 6. React page

```jsx
// frontend/Pages/Admin/Permissions/Index.jsx
import { Head } from "@inertiajs/react"
import { PageHeader } from "@/Components/admin/PageHeader"
import { SearchBar } from "@/Components/admin/SearchBar"
import { DataTablePagination } from "@/Components/admin/DataTablePagination"
import { useListFilters } from "@/composables/useListFilters"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function PermissionsIndex({ permissions, pagination, filters }) {
  const { search, setSearch, pageUrl } = useListFilters("admin_permissions", filters)
  return (
    <>
      <Head title="Permissions" />
      <PageHeader title="Permissions" description="Every permission Django knows about." />
      <SearchBar value={search} onChange={setSearch} placeholder="Filter permissions…" />
      {/* render a <Table> like Pages/Admin/Groups/Index.jsx */}
      <DataTablePagination pagination={pagination} buildUrl={pageUrl} itemLabel="permissions" />
    </>
  )
}

PermissionsIndex.layout = (page) => <AdminLayout breadcrumbs={[{ label: "Permissions" }]}>{page}</AdminLayout>
```

The file path under `Pages/` must match the component name passed to `render()`.

### 7. Tests

Every feature needs a selector test, a service test and — when permissions are involved — a policy test. Add a view test for anything with request parsing or redirects. See [Testing](testing.md).

## Why Inertia instead of a REST API?

- One router (Django's), one auth system (sessions), one place for permissions.
- No duplicated validation or serializers for page rendering.
- Pages still navigate without full reloads, with shared layouts that stay mounted.

Add a JSON API only for genuinely external consumers (mobile apps, webhooks, third parties).
