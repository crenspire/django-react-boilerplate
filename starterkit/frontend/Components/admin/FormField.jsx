import * as React from "react"
import { Label } from "@/Components/ui/label"
import { cn } from "@/lib/utils"

export function FormField({ label, error, htmlFor, required, children, className }) {
  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={htmlFor}>
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </Label>
      {children}
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
