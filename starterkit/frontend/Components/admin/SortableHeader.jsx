import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react"
import { Button } from "@/Components/ui/button"

/** Column header that cycles ascending → descending (shadcn data-table style). */
export function SortableHeader({ field, currentOrderBy, label, onSort }) {
  const direction = currentOrderBy === field ? "asc" : currentOrderBy === `-${field}` ? "desc" : null
  const Icon = direction === "asc" ? ArrowUp : direction === "desc" ? ArrowDown : ChevronsUpDown

  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      className="-ml-2.5 h-8 px-2.5 font-medium text-muted-foreground data-[active=true]:text-foreground"
      data-active={direction !== null}
      aria-sort={direction === "asc" ? "ascending" : direction === "desc" ? "descending" : "none"}
      onClick={() => onSort(direction === "asc" ? `-${field}` : field)}
    >
      {label}
      <Icon className={direction ? "" : "opacity-50"} />
    </Button>
  )
}
