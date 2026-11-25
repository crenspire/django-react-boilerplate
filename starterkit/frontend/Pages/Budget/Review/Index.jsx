import * as React from "react"
import { Head, Link, useForm } from "@inertiajs/react"
import { Check, Inbox, X } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/Components/ui/table"
import { DataTablePagination } from "@/Components/admin/DataTablePagination"
import { PageHeader } from "@/Components/admin/PageHeader"
import { ReviewDialog } from "@/Components/budget/ReviewDialog"
import { StatusBadge } from "@/Components/budget/StatusBadge"
import { useRoute } from "@/composables/useRoute"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"
import { formatRelativeTime } from "@/lib/date"
import { formatAmount } from "@/lib/money"
import { cn } from "@/lib/utils"

const TABS = [
  { key: "pending", label: "Pending" },
  { key: "history", label: "History" },
]

export default function ReviewIndex({ tab, requests, pagination, counts, pending_amount }) {
  const route = useRoute()
  const [target, setTarget] = React.useState(null)
  const form = useForm({ decision: "", note: "", tab })
  const isPending = tab === "pending"

  const openReview = (request, decision) => {
    form.clearErrors()
    form.setData({ decision, note: "", tab })
    setTarget(request)
  }

  const submitReview = () => {
    form.post(route("budget_review", { request_id: target.id }), {
      preserveScroll: true,
      onSuccess: () => setTarget(null),
    })
  }

  return (
    <>
      <Head title="Review queue" />
      <PageHeader
        title="Review queue"
        description={`${counts.pending} pending ${counts.pending === 1 ? "request" : "requests"} totalling ${formatAmount(pending_amount)}.`}
      />

      <div className="flex gap-1 border-b">
        {TABS.map((t) => (
          <Link
            key={t.key}
            href={route("budget_review_queue", {}, { tab: t.key })}
            preserveScroll
            className={cn(
              "-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors",
              tab === t.key ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t.label} <span className="ml-1 text-xs text-muted-foreground">{counts[t.key]}</span>
          </Link>
        ))}
      </div>

      <div className="flex flex-col gap-4">
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow className="hover:bg-transparent">
                <TableHead>Request</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="hidden md:table-cell">{isPending ? "Justification" : "Decision"}</TableHead>
                {isPending && (
                  <TableHead className="text-right">
                    <span className="sr-only">Actions</span>
                  </TableHead>
                )}
              </TableRow>
            </TableHeader>
            <TableBody>
              {!requests.length && (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={5} className="h-40">
                    <div className="flex flex-col items-center gap-2 text-center">
                      <Inbox className="h-8 w-8 text-muted-foreground" />
                      <p className="font-medium">{isPending ? "Nothing to review" : "No decisions yet"}</p>
                      <p className="text-sm text-muted-foreground">
                        {isPending ? "New requests from clients will appear here." : "Approved and rejected requests will appear here."}
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
              {requests.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="max-w-xs">
                    <Link
                      href={route("budget_review", { request_id: r.id })}
                      className="block truncate font-medium underline-offset-4 hover:underline"
                    >
                      {r.title}
                    </Link>
                    <p className="text-xs text-muted-foreground">
                      {r.requester} · {formatRelativeTime(r.created_at)}
                    </p>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{formatAmount(r.amount)}</TableCell>
                  <TableCell>
                    <StatusBadge status={r.status} label={r.status_label} />
                  </TableCell>
                  <TableCell className="hidden max-w-sm md:table-cell">
                    {isPending ? (
                      <p className="line-clamp-2 text-sm text-muted-foreground">{r.justification}</p>
                    ) : (
                      <div className="text-sm">
                        <p className="line-clamp-2">{r.review_note || <span className="text-muted-foreground">No note</span>}</p>
                        <p className="text-xs text-muted-foreground">
                          {r.reviewer ?? "Former user"} · {formatRelativeTime(r.reviewed_at)}
                        </p>
                      </div>
                    )}
                  </TableCell>
                  {isPending && (
                    <TableCell>
                      {r.can.review && (
                        <div className="flex justify-end gap-2">
                          <Button size="sm" variant="outline" onClick={() => openReview(r, "REJECTED")}>
                            <X />
                            Reject
                          </Button>
                          <Button size="sm" onClick={() => openReview(r, "APPROVED")}>
                            <Check />
                            Approve
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <DataTablePagination
          pagination={pagination}
          buildUrl={(page) => route("budget_review_queue", {}, { tab, page })}
          itemLabel="requests"
        />
      </div>

      <ReviewDialog
        request={target}
        decision={form.data.decision}
        note={form.data.note}
        onNoteChange={(value) => form.setData("note", value)}
        onConfirm={submitReview}
        onOpenChange={(open) => !open && setTarget(null)}
        processing={form.processing}
        error={form.errors.note}
      />
    </>
  )
}

ReviewIndex.layout = (page) => <WorkspaceLayout breadcrumbs={[{ label: "Review queue" }]}>{page}</WorkspaceLayout>
