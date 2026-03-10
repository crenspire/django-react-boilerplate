import * as React from "react"
import { Link } from "@inertiajs/react"
import { cn } from "@/lib/utils"

export function PageHeader({ title, breadcrumbs = [], children: actions }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        {breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1.5 text-sm text-muted-foreground mb-1">
            {breadcrumbs.map((crumb, i) => (
              <React.Fragment key={i}>
                <Link href={crumb.href} className="hover:text-foreground transition-colors">
                  {crumb.label}
                </Link>
                <span>/</span>
              </React.Fragment>
            ))}
            <span className="text-foreground">{title}</span>
          </nav>
        )}
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}
