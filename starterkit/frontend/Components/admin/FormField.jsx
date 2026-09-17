import { Label } from "@/Components/ui/label"
import { cn } from "@/lib/utils"

export function FormField({ label, error, htmlFor, required, description, children, className }) {
  return (
    <div className={cn("grid content-start gap-2", className)}>
      <Label htmlFor={htmlFor} className={error ? "text-destructive" : undefined}>
        {label}
        {required && <span className="ml-0.5 text-destructive">*</span>}
      </Label>
      {children}
      {description && !error && <p className="text-[0.8rem] text-muted-foreground">{description}</p>}
      {error && <p className="text-[0.8rem] font-medium text-destructive">{error}</p>}
    </div>
  )
}
