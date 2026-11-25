import * as React from "react"
import { Head, Link, router } from "@inertiajs/react"
import { FileText, Pencil, Plus, Undo2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/Components/ui/table"
import { DataTablePagination } from "@/Components/admin/DataTablePagination"
import { DeleteConfirmDialog } from "@/Components/admin/DeleteConfirmDialog"
import { PageHeader } from "@/Components/admin/PageHeader"
import { StatusBadge } from "@/Components/budget/StatusBadge"
import { useRoute } from "@/composables/useRoute"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"
import { formatRelativeTime } from "@/lib/date"
import { formatAmount } from "@/lib/money"

export default function MyRequestsIndex({ requests, pagination, can }) {
  const route = useRoute()
  const [withdrawTarget, setWithdrawTarget] = React.useState(null)
  const [withdrawing, setWithdrawing] = React.useState(false)

  const confirmWithdraw = () => {
    router.post(route("budget_request_withdraw", { request_id: withdrawTarget.id }), {}, {
      preserveScroll: true,
      onStart: () => setWithdrawing(true),
      onFinish: () => {
        setWithdrawing(false)
        setWithdrawTarget(null)
      },
    })
  }

  return (
    <>
      <Head title="My requests" />
      <PageHeader title="My requests" description="Track your budget requests and the decisions on them.">
        {can.create && (
          <Button asChild>
            <Link href={route("budget_request_create")}>
              <Plus />
              New request
            </Link>
          </Button>
        )}
      </PageHeader>

      <div className="flex flex-col gap-4">
        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow className="hover:bg-transparent">
                <TableHead>Request</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="hidden md:table-cell">Reviewer feedback</TableHead>
                <TableHead className="w-12">
                  <span className="sr-only">Actions</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!requests.length && (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={5} className="h-40">
                    <div className="flex flex-col items-center gap-2 text-center">
                      <FileText className="h-8 w-8 text-muted-foreground" />
                      <p className="font-medium">No requests yet</p>
                      <p className="text-sm text-muted-foreground">Submit your first budget request to get started.</p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
              {requests.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="max-w-xs">
                    <p className="truncate font-medium">{r.title}</p>
                    <p className="text-xs text-muted-foreground">Submitted {formatRelativeTime(r.created_at)}</p>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{formatAmount(r.amount)}</TableCell>
                  <TableCell>
                    <StatusBadge status={r.status} label={r.status_label} />
                  </TableCell>
                  <TableCell className="hidden max-w-sm md:table-cell">
                    {r.reviewer ? (
                      <div className="text-sm">
                        <p className="whitespace-pre-line">{r.review_note || <span className="text-muted-foreground">No note</span>}</p>
                        <p className="text-xs text-muted-foreground">— {r.reviewer}</p>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1">
                      {r.can.edit && (
                        <Button variant="ghost" size="icon" className="h-8 w-8" asChild>
                          <Link href={route("budget_request_edit", { request_id: r.id })} aria-label={`Edit ${r.title}`}>
                            <Pencil />
                          </Link>
                        </Button>
                      )}
                      {r.can.withdraw && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-destructive hover:text-destructive"
                          onClick={() => setWithdrawTarget(r)}
                          aria-label={`Withdraw ${r.title}`}
                        >
                          <Undo2 />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <DataTablePagination
          pagination={pagination}
          buildUrl={(page) => route("budget_my_requests", {}, { page })}
          itemLabel="requests"
        />
      </div>

      <DeleteConfirmDialog
        open={!!withdrawTarget}
        onOpenChange={(open) => !open && setWithdrawTarget(null)}
        onConfirm={confirmWithdraw}
        processing={withdrawing}
        title="Withdraw request"
        description={`Withdraw "${withdrawTarget?.title}"? It will no longer be reviewed, and this cannot be undone.`}
        confirmLabel="Withdraw"
        processingLabel="Withdrawing..."
      />
    </>
  )
}

MyRequestsIndex.layout = (page) => <WorkspaceLayout breadcrumbs={[{ label: "My requests" }]}>{page}</WorkspaceLayout>
