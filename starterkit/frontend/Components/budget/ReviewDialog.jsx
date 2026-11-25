import { Loader2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/Components/ui/dialog"
import { Textarea } from "@/Components/ui/textarea"
import { FormField } from "@/Components/admin/FormField"
import { formatAmount } from "@/lib/money"

const COPY = {
  APPROVED: { title: "Approve request", action: "Approve", label: "Note (optional)", variant: "default" },
  REJECTED: { title: "Reject request", action: "Reject", label: "Reason for rejection", variant: "destructive" },
}

export function ReviewDialog({ request, decision, note, onNoteChange, onConfirm, onOpenChange, processing, error }) {
  const copy = COPY[decision] ?? COPY.APPROVED
  const isReject = decision === "REJECTED"

  const handleSubmit = (e) => {
    e.preventDefault()
    onConfirm()
  }

  return (
    <Dialog open={!!request} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit} className="grid gap-4">
          <DialogHeader>
            <DialogTitle>{copy.title}</DialogTitle>
            <DialogDescription>
              {request && `"${request.title}" from ${request.requester} for ${formatAmount(request.amount)}. This decision is final.`}
            </DialogDescription>
          </DialogHeader>
          <FormField label={copy.label} htmlFor="review-note" error={error} required={isReject}>
            <Textarea
              id="review-note"
              value={note}
              onChange={(e) => onNoteChange(e.target.value)}
              rows={4}
              maxLength={2000}
              required={isReject}
              autoFocus
            />
          </FormField>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" variant={copy.variant} disabled={processing}>
              {processing && <Loader2 className="animate-spin" />}
              {copy.action}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
