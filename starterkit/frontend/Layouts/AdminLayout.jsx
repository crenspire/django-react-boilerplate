import { AppShell } from "@/Layouts/AppShell"

const ROOT = { label: "Admin", route: "admin_dashboard", subtitle: "Admin console" }

export function AdminLayout({ breadcrumbs, children }) {
  return (
    <AppShell root={ROOT} breadcrumbs={breadcrumbs}>
      {children}
    </AppShell>
  )
}
