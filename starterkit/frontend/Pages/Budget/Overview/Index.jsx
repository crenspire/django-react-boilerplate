import * as React from "react"
import { Head, Link, router } from "@inertiajs/react"
import { Inbox, Trash2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/Components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/Components/ui/table"
import { DataTablePagination } from "@/Components/admin/DataTablePagination"
import { DeleteConfirmDialog } from "@/Components/admin/DeleteConfirmDialog"
import { PageHeader } from "@/Components/admin/PageHeader"
import { StatusBadge } from "@/Components/budget/StatusBadge"
import { useRoute } from "@/composables/useRoute"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"
import { formatRelativeTime } from "@/lib/date"
import { formatAmount } from "@/lib/money"
import { cn } from "@/lib/utils"

const SUMMARY_CARDS = ["pending", "approved", "rejected", "withdrawn"]

function SummaryCard({ item, highlight }) {
  return (
    <Card className={cn("shadow-sm", highlight && "bg-gradient-to-t from-primary/[0.04] to-card dark:from-primary/[0.08]")}>
      <CardHeader className="space-y-2 pb-3">
        <CardDescription>{item.label}</CardDescription>
        <CardTitle className="text-2xl font-semibold tabular-nums">{formatAmount(item.amount)}</CardTitle>
      </CardHeader>
      <CardFooter className="text-sm text-muted-foreground">
        {item.count} {item.count === 1 ? "request" : "requests"}
      </CardFooter>
    </Card>
  )
}

export default function OverviewIndex({ summary, status, statuses, requests, pagination }) {
  const route = useRoute()
  const [deleteTarget, setDeleteTarget] = React.useState(null)
  const [deleting, setDeleting] = React.useState(false)
  const filters = [{ value: "", label: "All" }, ...statuses]

  const confirmDelete = () => {
    router.post(route("budget_request_delete", { request_id: deleteTarget.id }), { status }, {
      preserveScroll: true,
      onStart: () => setDeleting(true),
      onFinish: () => {
        setDeleting(false)
        setDeleteTarget(null)
      },
    })
  }

  return (
    <>
      <Head title="Budget overview" />
      <PageHeader
        title="Budget overview"
        description={`${summary.total.count} ${summary.total.count === 1 ? "request" : "requests"} across the organization.`}
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {SUMMARY_CARDS.map((key) => (
          <SummaryCard key={key} item={summary[key]} highlight={key === "pending" || key === "approved"} />
        ))}
      </div>

      <div className="flex gap-1 overflow-x-auto border-b">
        {filters.map((f) => (
          <Link
            key={f.value || "all"}
            href={route("budget_overview", {}, f.value ? { status: f.value } : {})}
            preserveScroll
            className={cn(
              "-mb-px whitespace-nowrap border-b-2 px-4 py-2 text-sm font-medium transition-colors",
              status === f.value ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {f.label}
            <span className="ml-1 text-xs text-muted-foreground">
              {f.value ? summary[f.value.toLowerCase()].count : summary.total.count}
            </span>
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
                <TableHead className="hidden md:table-cell">Decision</TableHead>
                <TableHead className="text-right">
                  <span className="sr-only">Actions</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!requests.length && (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={5} className="h-40">
                    <div className="flex flex-col items-center gap-2 text-center">
                      <Inbox className="h-8 w-8 text-muted-foreground" />
                      <p className="font-medium">No requests</p>
                      <p className="text-sm text-muted-foreground">Budget requests from clients will appear here.</p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
              {requests.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="max-w-xs">
                    <p className="truncate font-medium">{r.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {r.requester} · {formatRelativeTime(r.created_at)}
                    </p>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{formatAmount(r.amount)}</TableCell>
                  <TableCell>
                    <StatusBadge status={r.status} label={r.status_label} />
                  </TableCell>
                  <TableCell className="hidden max-w-sm md:table-cell">
                    {r.reviewed_at ? (
                      <div className="text-sm">
                        <p className="line-clamp-2">{r.review_note || <span className="text-muted-foreground">No note</span>}</p>
                        <p className="text-xs text-muted-foreground">
                          {r.reviewer ?? "Former user"} · {formatRelativeTime(r.reviewed_at)}
                        </p>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
                    {r.can.delete && (
                      <div className="flex justify-end">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-destructive hover:text-destructive"
                          onClick={() => setDeleteTarget(r)}
                        >
                          <Trash2 />
                          Delete
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        <DataTablePagination
          pagination={pagination}
          buildUrl={(page) => route("budget_overview", {}, status ? { status, page } : { page })}
          itemLabel="requests"
        />
      </div>

      <DeleteConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        onConfirm={confirmDelete}
        processing={deleting}
        title="Delete request permanently"
        description={`Delete "${deleteTarget?.title}" from ${deleteTarget?.requester}? It will be removed from every report, and this cannot be undone.`}
        confirmLabel="Delete permanently"
      />
    </>
  )
}

OverviewIndex.layout = (page) => <WorkspaceLayout breadcrumbs={[{ label: "Budget overview" }]}>{page}</WorkspaceLayout>
