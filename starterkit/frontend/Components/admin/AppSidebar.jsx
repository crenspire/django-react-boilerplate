import { Link } from "@inertiajs/react"
import { Layers } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/Components/ui/sidebar"
import { SidebarNav } from "@/Components/admin/SidebarNav"
import { UserMenu } from "@/Components/admin/UserMenu"

export function AppSidebar({ homeHref, navItems, user, isMobile, theme, onToggleTheme, onLogout, onNavigate }) {
  return (
    <Sidebar variant="inset" collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild tooltip="Dashboard">
              <Link href={homeHref} onClick={onNavigate}>
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <Layers className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold">Django Inertia</span>
                  <span className="truncate text-xs text-muted-foreground">Admin console</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarNav items={navItems} onNavigate={onNavigate} />
      </SidebarContent>
      <SidebarFooter>
        <UserMenu user={user} isMobile={isMobile} theme={theme} onToggleTheme={onToggleTheme} onLogout={onLogout} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
