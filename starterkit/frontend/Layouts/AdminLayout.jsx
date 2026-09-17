import * as React from "react"
import { router, usePage } from "@inertiajs/react"
import { LayoutDashboard, Shield, Users } from "lucide-react"
import { toast } from "sonner"
import { SidebarInset, SidebarProvider } from "@/Components/ui/sidebar"
import { Toaster } from "@/Components/ui/sonner"
import { AppSidebar } from "@/Components/admin/AppSidebar"
import { NavSearchDialog } from "@/Components/admin/NavSearchDialog"
import { SiteHeader } from "@/Components/admin/SiteHeader"
import { useIsMobile } from "@/composables/useIsMobile"
import { useRoute } from "@/composables/useRoute"
import { useSidebar } from "@/composables/useSidebar"
import { useTheme } from "@/composables/useTheme"
import { isActivePath } from "@/lib/route"

const NAV_ICONS = {
  dashboard: LayoutDashboard,
  users: Users,
  groups: Shield,
}

const TOASTS = {
  success: toast.success,
  error: toast.error,
  warning: toast.warning,
}

/**
 * Admin shell (shadcn "sidebar inset" layout). Pages opt in with
 * `Page.layout = (page) => <AdminLayout breadcrumbs={[...]}>{page}</AdminLayout>`;
 * the component type never changes, so Inertia keeps it mounted across visits.
 *
 * `breadcrumbs` are { label, route?, params? }; the last entry is the current page.
 */
export function AdminLayout({ breadcrumbs = [], children }) {
  const { props, url } = usePage()
  const route = useRoute()
  const isMobile = useIsMobile()
  const { theme, toggle: toggleTheme } = useTheme()
  const sidebar = useSidebar(isMobile)
  const [searchOpen, setSearchOpen] = React.useState(false)

  const navItems = React.useMemo(
    () =>
      (props.admin_nav ?? []).map((item) => {
        const href = route(item.route)
        return {
          section: item.section,
          label: item.label,
          href,
          icon: NAV_ICONS[item.icon] ?? LayoutDashboard,
          active: isActivePath(url, href, { exact: item.route === "admin_dashboard" }),
        }
      }),
    [props.admin_nav, route, url]
  )

  const resolvedBreadcrumbs = React.useMemo(
    () => [
      { label: "Admin", href: route("admin_dashboard") },
      ...breadcrumbs.map((crumb) => ({
        label: crumb.label,
        href: crumb.route ? route(crumb.route, crumb.params) : undefined,
      })),
    ],
    [breadcrumbs, route]
  )

  // Django messages arrive as the shared `flash` prop; show each once as a toast.
  React.useEffect(() => {
    for (const { level, message } of props.flash ?? []) {
      ;(TOASTS[level] ?? toast)(message)
    }
  }, [props.flash])

  React.useEffect(() => {
    const handleKeydown = (event) => {
      if (event.key === "k" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        setSearchOpen((prev) => !prev)
      }
    }
    window.addEventListener("keydown", handleKeydown)
    return () => window.removeEventListener("keydown", handleKeydown)
  }, [])

  const logout = () => router.post(route("logout"))
  const closeMobileSidebar = () => {
    if (isMobile) sidebar.setOpenMobile(false)
  }

  return (
    <SidebarProvider
      open={sidebar.open}
      onOpenChange={sidebar.setOpen}
      openMobile={sidebar.openMobile}
      onOpenMobileChange={sidebar.setOpenMobile}
      isMobile={isMobile}
    >
      <AppSidebar
        homeHref={route("admin_dashboard")}
        navItems={navItems}
        user={props.auth?.user}
        isMobile={isMobile}
        theme={theme}
        onToggleTheme={toggleTheme}
        onLogout={logout}
        onNavigate={closeMobileSidebar}
      />
      <SidebarInset>
        <SiteHeader
          breadcrumbs={resolvedBreadcrumbs}
          theme={theme}
          onToggleTheme={toggleTheme}
          onOpenSearch={() => setSearchOpen(true)}
        />
        <div className="flex flex-1 flex-col gap-6 p-4 lg:p-6">{children}</div>
      </SidebarInset>
      <NavSearchDialog
        open={searchOpen}
        onOpenChange={setSearchOpen}
        items={navItems}
        theme={theme}
        onNavigate={(href) => router.visit(href)}
        onToggleTheme={toggleTheme}
        onLogout={logout}
      />
      <Toaster theme={theme} position="bottom-right" />
    </SidebarProvider>
  )
}
