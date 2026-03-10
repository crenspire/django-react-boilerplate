import * as React from "react"
import { Link, usePage, router } from "@inertiajs/react"
import {
  LayoutDashboard,
  Users,
  Shield,
  LogOut,
  ChevronDown,
  Search,
  Sun,
  Moon,
  Settings,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react"
import { Avatar, AvatarFallback } from "@/Components/ui/avatar"
import { Button } from "@/Components/ui/button"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/Components/ui/dropdown-menu"
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/Components/ui/tooltip"
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/Components/ui/dialog"
import { useTheme } from "@/composables/useTheme"
import { useSidebar } from "@/composables/useSidebar"
import { useIsMobile } from "@/composables/useIsMobile"
import { cn } from "@/lib/utils"

const iconUrl = typeof window !== "undefined" ? `${window.location.origin}/static/icon.svg` : ""

const ALL_NAV_ITEMS = [
  { href: "/admin/", label: "Dashboard", icon: LayoutDashboard, section: "General" },
  { href: "/admin/users/", label: "Users", icon: Users, section: "General" },
  { href: "/admin/groups/", label: "Groups", icon: Shield, section: "General" },
  { href: "#", label: "Settings", icon: Settings, section: "Other" },
]

const GENERAL_NAV_ITEMS = [
  { href: "/admin/", label: "Dashboard", icon: LayoutDashboard, match: (url) => url === "/admin/" },
  {
    href: "/admin/users/",
    label: "Users",
    icon: Users,
    match: (url) => typeof url === "string" && url.startsWith("/admin/users"),
  },
  {
    href: "/admin/groups/",
    label: "Groups",
    icon: Shield,
    match: (url) => typeof url === "string" && url.startsWith("/admin/groups"),
  },
]

function getDisplayName(user) {
  if (!user) return "User"
  const first = user.first_name ?? ""
  const last = user.last_name ?? ""
  const full = [first, last].filter(Boolean).join(" ")
  if (full) return full
  if (user.username) return user.username
  if (user.email) return user.email
  return "User"
}

function getUserInitials(user) {
  if (!user) return "U"
  const first = user.first_name ?? ""
  const last = user.last_name ?? ""
  if (first && last) return `${first[0]}${last[0]}`.toUpperCase()
  if (first) return first.slice(0, 2).toUpperCase()
  const name = user.username || user.email || ""
  if (name) return name.slice(0, 2).toUpperCase()
  return "U"
}

export function AdminLayout({ auth: layoutAuth, children }) {
  const page = usePage()
  const authUser = layoutAuth?.user ?? page.props?.auth?.user ?? null
  const { theme, toggle: toggleTheme } = useTheme()
  const { sidebarOpen, toggle: toggleSidebar, close: closeSidebar } = useSidebar()
  const isMobile = useIsMobile()

  const [searchOpen, setSearchOpen] = React.useState(false)
  const [searchQuery, setSearchQuery] = React.useState("")
  const searchInputRef = React.useRef(null)

  const currentUrl = (() => {
    const u = page.url
    if (typeof u === "string") return u
    if (u != null && typeof u === "object" && typeof u.pathname === "string") return u.pathname
    return ""
  })()

  React.useEffect(() => {
    if (searchOpen) {
      setSearchQuery("")
      searchInputRef.current?.focus()
    }
  }, [searchOpen])

  React.useEffect(() => {
    const handleGlobalKeydown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setSearchOpen((prev) => {
          if (!prev) setSearchQuery("")
          return !prev
        })
      }
    }
    window.addEventListener("keydown", handleGlobalKeydown)
    return () => window.removeEventListener("keydown", handleGlobalKeydown)
  }, [])

  const filteredNavItems = React.useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    if (!q) return ALL_NAV_ITEMS
    return ALL_NAV_ITEMS.filter(
      (item) =>
        item.label.toLowerCase().includes(q) || item.section.toLowerCase().includes(q)
    )
  }, [searchQuery])

  const displayName = getDisplayName(authUser)
  const userInitials = getUserInitials(authUser)
  const userEmail = authUser?.email || "No email"

  const logout = () => router.post("/logout/")

  const closeSearch = () => setSearchOpen(false)

  const handleSearchKeydown = (e) => {
    if (e.key === "Escape") closeSearch()
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile backdrop: dims content and closes sidebar on click */}
      <button
        type="button"
        aria-label="Close menu"
        className={cn(
          "fixed inset-0 z-40 bg-black/60 transition-opacity duration-200 md:hidden",
          sidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={closeSidebar}
      />
      <aside
        className={cn(
          "flex flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground shrink-0 transition-all duration-200 ease-out overflow-hidden",
          "fixed inset-y-0 left-0 z-50 w-64",
          "md:relative md:translate-x-0",
          sidebarOpen ? "translate-x-0 md:w-64" : "-translate-x-full md:translate-x-0 md:w-16"
        )}
      >
        <TooltipProvider delayDuration={300}>
          <div
            className={cn(
              "flex border-b border-sidebar-border shrink-0",
              sidebarOpen ? "items-center gap-3 p-4 h-14" : "justify-center py-4 px-0 h-14"
            )}
          >
            {iconUrl && (
              <img src={iconUrl} alt="" className="h-8 w-8 shrink-0 rounded-lg object-contain" />
            )}
            {sidebarOpen && (
              <div className="flex flex-col min-w-0">
                <span className="font-semibold text-sm truncate">Admin</span>
                <span className="text-xs text-muted-foreground truncate">Django + Inertia</span>
              </div>
            )}
          </div>

          <nav className="flex-1 overflow-y-auto py-3">
            {sidebarOpen && (
              <div className="px-3 mb-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">
                  General
                </p>
              </div>
            )}
            <div
              className={cn(
                "space-y-0.5",
                sidebarOpen ? "px-2" : "px-2 flex flex-col items-center"
              )}
            >
              {GENERAL_NAV_ITEMS.map((item) => {
                const linkClass = cn(
                  "flex items-center rounded-md text-sm font-medium transition-colors",
                  sidebarOpen ? "gap-3 px-3 py-2 w-full" : "justify-center p-2 w-10 h-10",
                  item.match(currentUrl)
                    ? "bg-accent text-accent-foreground"
                    : "text-sidebar-foreground hover:bg-accent/50 hover:text-accent-foreground"
                )
                const linkContent = (
                  <>
                    <item.icon className="h-4 w-4 shrink-0" />
                    {sidebarOpen && <span className="truncate">{item.label}</span>}
                  </>
                )
                if (!sidebarOpen) {
                  return (
                    <Tooltip key={item.href} delayDuration={0}>
                      <TooltipTrigger asChild>
                        <Link
                          href={item.href}
                          className={linkClass}
                          onClick={() => isMobile && closeSidebar()}
                        >
                          {linkContent}
                        </Link>
                      </TooltipTrigger>
                      <TooltipContent side="right" className="border-sidebar-border">
                        {item.label}
                      </TooltipContent>
                    </Tooltip>
                  )
                }
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={linkClass}
                    onClick={() => isMobile && closeSidebar()}
                  >
                    {linkContent}
                  </Link>
                )
              })}
            </div>
            {sidebarOpen && (
              <div className="px-3 mt-6 mb-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wider">
                  Other
                </p>
              </div>
            )}
            <div
              className={cn(
                "space-y-0.5",
                sidebarOpen ? "px-2" : "px-2 flex flex-col items-center"
              )}
            >
              {!sidebarOpen ? (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <span className="flex justify-center p-2 w-10 h-10 rounded-md text-muted-foreground cursor-not-allowed">
                      <Settings className="h-4 w-4 shrink-0" />
                    </span>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="border-sidebar-border">
                    Settings
                  </TooltipContent>
                </Tooltip>
              ) : (
                <span className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground cursor-not-allowed">
                  <Settings className="h-4 w-4 shrink-0" />
                  Settings
                </span>
              )}
            </div>
          </nav>

          <div
            className={cn(
              "border-t border-sidebar-border shrink-0",
              sidebarOpen ? "p-3" : "p-2 flex justify-center"
            )}
          >
            <DropdownMenu>
              {!sidebarOpen ? (
                <Tooltip>
                  <TooltipTrigger asChild>
                    <DropdownMenuTrigger asChild>
                      <button className="flex rounded-md hover:bg-accent/50 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring p-2">
                        <Avatar className="h-8 w-8 shrink-0">
                          <AvatarFallback className="bg-primary/10 text-primary text-xs">
                            {userInitials}
                          </AvatarFallback>
                        </Avatar>
                      </button>
                    </DropdownMenuTrigger>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="border-sidebar-border">
                    {displayName}
                  </TooltipContent>
                </Tooltip>
              ) : (
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-3 w-full rounded-md px-3 py-2 text-sm hover:bg-accent/50 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring">
                    <Avatar className="h-8 w-8 shrink-0">
                      <AvatarFallback className="bg-primary/10 text-primary text-xs">
                        {userInitials}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 text-left min-w-0">
                      <p className="font-medium truncate text-sidebar-foreground">{displayName}</p>
                      <p className="text-xs text-muted-foreground truncate">{userEmail}</p>
                    </div>
                    <ChevronDown className="h-4 w-4 shrink-0 opacity-50" />
                  </button>
                </DropdownMenuTrigger>
              )}
              <DropdownMenuContent side="top" align="start" className="w-56">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-destructive cursor-pointer"
                  onClick={logout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </TooltipProvider>
      </aside>

      <div
        className={cn(
          "flex flex-1 flex-col min-w-0",
          isMobile && sidebarOpen && "z-30 relative"
        )}
      >
        <header className="flex h-14 shrink-0 items-center gap-2 sm:gap-4 border-b border-border bg-background px-3 sm:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 shrink-0"
            aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
            onClick={toggleSidebar}
          >
            {sidebarOpen ? (
              <PanelLeftClose className="h-4 w-4" />
            ) : (
              <PanelLeft className="h-4 w-4" />
            )}
          </Button>
          <div className="flex-1 min-w-0" />
          <div className="flex items-center gap-1 sm:gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 shrink-0 sm:hidden"
              aria-label="Search"
              onClick={() => setSearchOpen(true)}
            >
              <Search className="h-4 w-4" />
            </Button>
            <button
              type="button"
              className="relative hidden sm:flex items-center w-64 gap-2 rounded-md border border-input bg-muted/50 px-3 py-2 h-9 text-sm text-muted-foreground hover:bg-muted/80 hover:text-foreground transition-colors text-left"
              onClick={() => setSearchOpen(true)}
            >
              <Search className="h-4 w-4 shrink-0" />
              <span className="flex-1 truncate">Search...</span>
              <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-0.5 rounded border bg-background/80 px-1.5 font-mono text-[10px] font-medium">
                <span className="text-xs">⌘</span>K
              </kbd>
            </button>
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 shrink-0"
              onClick={toggleTheme}
            >
              {theme === "light" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9 shrink-0 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback className="bg-primary/10 text-primary text-xs">
                      {userInitials}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>My Account</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-destructive cursor-pointer"
                  onClick={logout}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <Dialog open={searchOpen} onOpenChange={setSearchOpen}>
          <DialogContent
            className="max-w-lg gap-0 p-0 overflow-hidden"
            onKeyDown={handleSearchKeydown}
            onPointerDownOutside={closeSearch}
          >
            <DialogTitle className="sr-only">Search and navigate</DialogTitle>
            <DialogDescription className="sr-only">
              Search or jump to a page. Sidebar menu options listed below.
            </DialogDescription>
            <div className="flex items-center border-b border-border px-3">
              <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
              <input
                ref={searchInputRef}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                type="text"
                placeholder="Search or jump to..."
                className="flex-1 bg-transparent py-3 px-3 text-sm outline-none placeholder:text-muted-foreground"
                autoFocus
              />
              <kbd className="hidden sm:inline-flex h-5 select-none items-center gap-0.5 rounded border bg-muted px-1.5 font-mono text-[10px] text-muted-foreground">
                Esc
              </kbd>
            </div>
            <div className="max-h-[min(60vh,400px)] overflow-y-auto py-2">
              {filteredNavItems.map((item, i) =>
                item.href !== "#" ? (
                  <Link
                    key={`${item.href}-${item.label}-${i}`}
                    href={item.href}
                    className="flex items-center gap-3 px-3 py-2.5 text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
                    onClick={closeSearch}
                  >
                    <item.icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <span className="font-medium">{item.label}</span>
                    <span className="text-xs text-muted-foreground ml-auto">{item.section}</span>
                  </Link>
                ) : (
                  <span
                    key={`${item.href}-${item.label}-${i}`}
                    className="flex items-center gap-3 px-3 py-2.5 text-sm text-muted-foreground cursor-not-allowed"
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    {item.label}
                    <span className="text-xs ml-auto">{item.section}</span>
                  </span>
                )
              )}
              {filteredNavItems.length === 0 && (
                <p className="px-3 py-4 text-sm text-muted-foreground">No matches.</p>
              )}
            </div>
          </DialogContent>
        </Dialog>

        <main className="flex-1 overflow-auto">
          <div className="p-4 sm:p-6">{children}</div>
        </main>
      </div>
    </div>
  )
}
