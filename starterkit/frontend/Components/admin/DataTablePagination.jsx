import * as React from "react"
import { Link } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

export function DataTablePagination({ pagination, buildUrl }) {
  if (!pagination || pagination.total_pages <= 1) return null

  const { page, total_pages } = pagination
  const prevUrl = buildUrl(page - 1)
  const nextUrl = buildUrl(page + 1)

  return (
    <div className="flex items-center justify-between px-2">
      <p className="text-sm text-muted-foreground">
        Page {page} of {total_pages}
      </p>
      <div className="flex items-center gap-2">
        {page > 1 ? (
          <Link href={prevUrl}>
            <Button variant="outline" size="sm">
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </Button>
          </Link>
        ) : (
          <Button variant="outline" size="sm" disabled>
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
        )}
        {page < total_pages ? (
          <Link href={nextUrl}>
            <Button variant="outline" size="sm">
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        ) : (
          <Button variant="outline" size="sm" disabled>
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        )}
      </div>
    </div>
  )
}
