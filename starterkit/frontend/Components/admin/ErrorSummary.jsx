import { AlertCircle } from "lucide-react"
import { Alert, AlertDescription } from "@/Components/ui/alert"
import { cn } from "@/lib/utils"

/**
 * Form-level errors: non-field messages from the backend, plus a hint when
 * field errors are shown inline below.
 */
export function ErrorSummary({ errors = {}, className }) {
  const nonFieldErrors = errors.non_field_errors ?? []
  const hasFieldErrors = Object.keys(errors).some((key) => key !== "non_field_errors")
  if (!nonFieldErrors.length && !hasFieldErrors) return null

  return (
    <Alert variant="destructive" className={cn("bg-destructive/5", className)}>
      <AlertCircle className="h-4 w-4" />
      <AlertDescription className="space-y-1">
        {nonFieldErrors.map((message) => (
          <p key={message}>{message}</p>
        ))}
        {hasFieldErrors && <p>Please correct the errors below.</p>}
      </AlertDescription>
    </Alert>
  )
}
