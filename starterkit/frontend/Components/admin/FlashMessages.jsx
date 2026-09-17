import { AlertCircle, CheckCircle2, Info } from "lucide-react"
import { Alert, AlertDescription } from "@/Components/ui/alert"

const ICONS = { success: CheckCircle2, error: AlertCircle }

/** Renders Django `messages` shared as the `flash` prop. */
export function FlashMessages({ messages = [] }) {
  if (!messages.length) return null

  return (
    <div className="space-y-2">
      {messages.map(({ level, message }, index) => {
        const Icon = ICONS[level] ?? Info
        return (
          <Alert key={`${index}-${message}`} variant={level === "error" ? "destructive" : "default"}>
            <Icon className="h-4 w-4" />
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )
      })}
    </div>
  )
}
