import * as React from "react"
import { router } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/Components/ui/dialog"

export function DeleteConfirmDialog({
  title = "Are you sure?",
  description = "This action cannot be undone.",
  deleteUrl,
  children,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
}) {
  const [internalOpen, setInternalOpen] = React.useState(false)
  const [processing, setProcessing] = React.useState(false)

  const isControlled = controlledOpen !== undefined && controlledOnOpenChange !== undefined
  const open = isControlled ? controlledOpen : internalOpen
  const setOpen = isControlled ? controlledOnOpenChange : setInternalOpen

  const confirmDelete = () => {
    setProcessing(true)
    router.post(deleteUrl, {}, {
      onFinish: () => {
        setProcessing(false)
        setOpen(false)
      },
    })
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {!isControlled && children ? <DialogTrigger asChild>{children}</DialogTrigger> : null}
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="destructive" disabled={processing} onClick={confirmDelete}>
            {processing ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
