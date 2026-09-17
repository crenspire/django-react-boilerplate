import { CircleCheck, CircleSlash, Crown, ShieldCheck } from "lucide-react"
import { Badge } from "@/Components/ui/badge"

export function StatusBadge({ active }) {
  return active ? (
    <Badge variant="outline" className="px-1.5 text-muted-foreground">
      <CircleCheck className="fill-success text-background" />
      Active
    </Badge>
  ) : (
    <Badge variant="outline" className="px-1.5 text-muted-foreground">
      <CircleSlash />
      Inactive
    </Badge>
  )
}

export function RoleBadge({ isStaff, isSuperuser }) {
  if (isSuperuser) {
    return (
      <Badge variant="secondary">
        <Crown />
        Superuser
      </Badge>
    )
  }
  if (isStaff) {
    return (
      <Badge variant="outline">
        <ShieldCheck />
        Staff
      </Badge>
    )
  }
  return <span className="text-sm text-muted-foreground">Member</span>
}
