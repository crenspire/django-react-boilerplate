import { Fragment } from "react"
import { Link } from "@inertiajs/react"
import { Moon, Search, Sun } from "lucide-react"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/Components/ui/breadcrumb"
import { Button } from "@/Components/ui/button"
import { Separator } from "@/Components/ui/separator"
import { SidebarTrigger } from "@/Components/ui/sidebar"

/**
 * Top bar inside the inset: sidebar trigger, breadcrumbs, search and theme toggle.
 * `breadcrumbs` are { label, href? }; the last one is the current page.
 */
export function SiteHeader({ breadcrumbs, theme, onToggleTheme, onOpenSearch }) {
  return (
    <header className="flex h-14 shrink-0 items-center gap-2 border-b px-4 lg:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mx-2 !h-4" />
      <Breadcrumb className="min-w-0">
        <BreadcrumbList className="flex-nowrap">
          {breadcrumbs.map((crumb, index) => {
            const isLast = index === breadcrumbs.length - 1
            return (
              <Fragment key={`${crumb.label}-${index}`}>
                <BreadcrumbItem className={isLast ? "min-w-0" : "hidden md:inline-flex"}>
                  {isLast || !crumb.href ? (
                    <BreadcrumbPage className="truncate">{crumb.label}</BreadcrumbPage>
                  ) : (
                    <BreadcrumbLink asChild>
                      <Link href={crumb.href}>{crumb.label}</Link>
                    </BreadcrumbLink>
                  )}
                </BreadcrumbItem>
                {!isLast && <BreadcrumbSeparator className="hidden md:block" />}
              </Fragment>
            )
          })}
        </BreadcrumbList>
      </Breadcrumb>

      <div className="ml-auto flex items-center gap-2">
        <Button
          variant="outline"
          onClick={onOpenSearch}
          className="relative hidden h-8 w-56 justify-start rounded-md bg-muted/50 px-3 text-sm font-normal text-muted-foreground shadow-none sm:flex lg:w-64"
        >
          <Search className="h-4 w-4" />
          <span>Search…</span>
          <kbd className="pointer-events-none absolute right-1.5 top-1/2 hidden h-5 -translate-y-1/2 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium sm:flex">
            <span className="text-xs">⌘</span>K
          </kbd>
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8 sm:hidden" onClick={onOpenSearch} aria-label="Search">
          <Search />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={onToggleTheme}
          aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        >
          {theme === "dark" ? <Sun /> : <Moon />}
        </Button>
      </div>
    </header>
  )
}
