import { CircleCheck, CircleSlash, CircleX, Clock } from "lucide-react"
import { Badge } from "@/Components/ui/badge"
import { cn } from "@/lib/utils"

const STYLES = {
  PENDING: { icon: Clock, className: "border-amber-500/40 text-amber-700 dark:text-amber-400" },
  APPROVED: { icon: CircleCheck, className: "border-success/50 text-success" },
  REJECTED: { icon: CircleX, className: "border-destructive/50 text-destructive" },
  WITHDRAWN: { icon: CircleSlash, className: "text-muted-foreground" },
}

export function StatusBadge({ status, label }) {
  const { icon: Icon, className } = STYLES[status] ?? STYLES.WITHDRAWN
  return (
    <Badge variant="outline" className={cn("px-1.5", className)}>
      <Icon />
      {label}
    </Badge>
  )
}
