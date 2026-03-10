import * as React from "react"
import { ArrowUp, ArrowDown, ArrowUpDown } from "lucide-react"

export function SortableHeader({ field, currentOrderBy, label, onSort }) {
  const sortDirection =
    currentOrderBy === field ? "asc" : currentOrderBy === `-${field}` ? "desc" : null

  const handleToggle = () => {
    if (sortDirection === "asc") {
      onSort?.(`-${field}`)
    } else {
      onSort?.(field)
    }
  }

  return (
    <button
      type="button"
      className="inline-flex items-center gap-1 hover:text-foreground transition-colors"
      onClick={handleToggle}
    >
      {label}
      {sortDirection === "asc" && <ArrowUp className="h-4 w-4" />}
      {sortDirection === "desc" && <ArrowDown className="h-4 w-4" />}
      {sortDirection == null && <ArrowUpDown className="h-4 w-4 opacity-50" />}
    </button>
  )
}
