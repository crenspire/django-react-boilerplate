# Frontend

The frontend is a React 18 app bundled by Vite, rendered through Inertia, and styled with Tailwind CSS 3 and [shadcn/ui](https://v3.shadcn.com) (new-york style, zinc palette, Geist font).

## Pages and layouts

Each Django view renders one component from `frontend/Pages/`. The name passed to `render()` is the path under `Pages/`:

```python
render(request, "Admin/Users/Index", props)   # → frontend/Pages/Admin/Users/Index.jsx
```

Pages receive their data **only** as props. They choose a layout with Inertia's persistent-layout pattern, so the layout stays mounted (sidebar state, open menus) while pages change:

```jsx
UsersEdit.layout = (page) => (
  <AdminLayout breadcrumbs={[{ label: "Users", route: "admin_users" }, { label: page.props.user.username }]}>
    {page}
  </AdminLayout>
)
```

| Layout | Used by | Contains |
|---|---|---|
| `AdminLayout` | `Pages/Admin/*` | Sidebar, header with breadcrumbs, ⌘K palette, toasts |
| `AuthLayout` | `Pages/Auth/*` | Split-screen sign-in shell |

## Admin shell

`AdminLayout` is built from the shadcn [Sidebar](https://v3.shadcn.com/docs/components/sidebar) block using the **inset** variant:

- **`AppSidebar`** — brand, navigation grouped by section, account menu (theme toggle, log out). Collapses to icons with tooltips (⌘B) and becomes a sheet on mobile.
- **`SiteHeader`** — sidebar trigger, breadcrumbs, search button and theme toggle.
- **`NavSearchDialog`** — ⌘K command palette built on `cmdk`.
- **Toasts** — Django messages arrive in the shared `flash` prop and are shown with [Sonner](https://sonner.emilkowal.ski/).

Navigation items come from the server (`admin_nav` prop), already filtered by permission. To add one, see [Architecture → Adding a feature](architecture.md#5-expose-the-route-and-add-it-to-the-sidebar).

## Shared props

`main/middleware.py` shares these with every page:

| Prop | Content |
|---|---|
| `auth.user` | `id`, `username`, `email`, `first_name`, `last_name` (or `null`) |
| `flash` | Django messages as `{ level, message }` |
| `routes` | Route names → URL templates (see below) |
| `admin_nav` | Sidebar items the user may open |

## Routes

Django owns routing, so React never hardcodes paths. Route names listed in `main/routes.py` are shared as URL templates and resolved with the `useRoute` hook:

```jsx
const route = useRoute()
route("admin_users")                                  // "/admin/users/"
route("admin_user_edit", { user_id: 7 })              // "/admin/users/7/edit/"
route("admin_users", {}, { search: "ava", page: 2 })  // "/admin/users/?search=ava&page=2"
```

Unknown names or missing parameters throw, so typos fail loudly.

## Components

| Folder | What goes there |
|---|---|
| `Components/ui/` | shadcn/ui primitives (Button, Card, Sidebar, Command, …). Keep them generic. |
| `Components/admin/` | App components (forms, tables, badges, page header). Presentational: data and callbacks come from props. |
| `composables/` | React hooks for UI-only state (`useTheme`, `useSidebar`, `useListFilters`, `useRoute`). |
| `lib/` | Pure functions with Vitest tests (`route`, `csrf`, `date`, `user`). |

Components must not call APIs or contain business rules; pages trigger requests with Inertia's `router` / `useForm`, and permission-dependent UI renders from `can` flags computed by services.

### Adding a shadcn/ui component

This project uses the **Tailwind v3** flavour of shadcn/ui in JavaScript, one folder per component:

1. Open the component on [v3.shadcn.com](https://v3.shadcn.com/docs/components) and copy the source.
2. Create `Components/ui/<name>/<Name>.jsx`, remove TypeScript types, and keep the `@/lib/utils` import for `cn`.
3. Add `Components/ui/<name>/index.js` re-exporting its parts.
4. Install any Radix package it needs with `npm install`.

### List pages

`useListFilters(routeName, filters)` gives list pages debounced search, sorting and pagination links while Django does the filtering:

```jsx
const { search, setSearch, sortBy, pageUrl } = useListFilters("admin_users", filters)
```

Pair it with `SearchBar`, `SortableHeader` and `DataTablePagination` as in `Pages/Admin/Users/Index.jsx`.

## Theming

Colours are CSS variables in `frontend/main.css` using shadcn/ui's token names (`--background`, `--primary`, `--sidebar`, …), with a `.dark` block for dark mode. To restyle the app:

- Paste a palette from the [shadcn themes page](https://v3.shadcn.com/themes) into `main.css` (keep the `--sidebar-*` and `--success` tokens).
- Change `--radius` for rounder or sharper corners.
- Swap the font by replacing the `@fontsource-variable/geist` import and `fontFamily.sans` in `tailwind.config.js`.

The chosen theme is stored in `localStorage` (`admin-theme`) and applied by an inline script in `templates/base.html` before first paint, so there is no flash.

## CSRF

Django's CSRF cookie (`csrftoken`) is read on every Inertia request and sent as `X-CSRFToken` (`frontend/app.jsx`, `lib/csrf.js`). Keep Django's default cookie name: `XSRF-TOKEN` is also used by Laravel and Angular apps and collides with them on shared hosts such as `localhost`.

## Scripts

```bash
npm run dev      # Vite dev server with HMR
npm run build    # production build + manifest into ../static/
npm run lint     # ESLint (React + hooks rules)
npm test         # Vitest
```
