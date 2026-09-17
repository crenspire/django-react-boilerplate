import { Link } from "@inertiajs/react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/Components/ui/button"

export function DataTablePagination({ pagination, buildUrl, itemLabel = "rows" }) {
  if (!pagination) return null
  const { page, page_size, total, total_pages } = pagination
  const first = total ? (page - 1) * page_size + 1 : 0
  const last = Math.min(page * page_size, total)

  return (
    <div className="flex items-center justify-between gap-4 px-1">
      <p className="text-sm text-muted-foreground">
        {total ? `Showing ${first}–${last} of ${total} ${itemLabel}` : `No ${itemLabel}`}
      </p>
      {total_pages > 1 && (
        <div className="flex items-center gap-2">
          <span className="hidden text-sm font-medium sm:inline">
            Page {page} of {total_pages}
          </span>
          <PageButton href={page > 1 ? buildUrl(page - 1) : null} label="Previous page">
            <ChevronLeft />
          </PageButton>
          <PageButton href={page < total_pages ? buildUrl(page + 1) : null} label="Next page">
            <ChevronRight />
          </PageButton>
        </div>
      )}
    </div>
  )
}

function PageButton({ href, label, children }) {
  if (!href) {
    return (
      <Button variant="outline" size="icon" className="h-8 w-8" disabled aria-label={label}>
        {children}
      </Button>
    )
  }
  return (
    <Button variant="outline" size="icon" className="h-8 w-8" asChild>
      <Link href={href} preserveScroll aria-label={label}>
        {children}
      </Link>
    </Button>
  )
}
