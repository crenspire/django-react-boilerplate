import { AppShell } from "@/Layouts/AppShell"

const ROOT = { label: "Workspace", route: "workspace", subtitle: "Budget requests" }

export function WorkspaceLayout({ breadcrumbs, children }) {
  return (
    <AppShell root={ROOT} breadcrumbs={breadcrumbs}>
      {children}
    </AppShell>
  )
}
