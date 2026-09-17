import * as React from "react"
import { cn } from "@/lib/utils"

const TableCell = React.forwardRef(({ className, ...props }, ref) => (
  <td ref={ref} className={cn("whitespace-nowrap px-3 py-2.5 align-middle [&:has([role=checkbox])]:pr-0", className)} {...props} />
))
TableCell.displayName = "TableCell"

export { TableCell }
