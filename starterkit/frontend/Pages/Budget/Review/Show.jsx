import { Head, Link, useForm } from "@inertiajs/react"
import { Check, Loader2, X } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/Components/ui/card"
import { Textarea } from "@/Components/ui/textarea"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { FormField } from "@/Components/admin/FormField"
import { PageHeader } from "@/Components/admin/PageHeader"
import { StatusBadge } from "@/Components/budget/StatusBadge"
import { useRoute } from "@/composables/useRoute"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"
import { formatRelativeTime } from "@/lib/date"
import { formatAmount } from "@/lib/money"

function Detail({ label, children }) {
  return (
    <div className="grid gap-1">
      <dt className="text-sm text-muted-foreground">{label}</dt>
      <dd className="text-sm">{children}</dd>
    </div>
  )
}

export default function ReviewShow({ request, form: initialForm, errors = {} }) {
  const route = useRoute()
  const form = useForm(initialForm)

  const submit = (decision) => {
    form.transform((data) => ({ ...data, decision }))
    form.post(route("budget_review", { request_id: request.id }))
  }

  return (
    <>
      <Head title={request.title} />
      <PageHeader title={request.title} description={`Submitted by ${request.requester} ${formatRelativeTime(request.created_at)}.`}>
        <StatusBadge status={request.status} label={request.status_label} />
      </PageHeader>
      <ErrorSummary errors={errors} className="max-w-3xl" />

      <div className="grid max-w-3xl gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Request</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid gap-4">
              <Detail label="Amount">
                <span className="text-lg font-semibold tabular-nums">{formatAmount(request.amount)}</span>
              </Detail>
              <Detail label="Business justification">
                <p className="whitespace-pre-line">{request.justification}</p>
              </Detail>
            </dl>
          </CardContent>
        </Card>

        {request.can.review ? (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Your decision</CardTitle>
              <CardDescription>A note is required when rejecting. Decisions are final.</CardDescription>
            </CardHeader>
            <CardContent>
              <FormField label="Note" htmlFor="note" error={errors.note?.[0]}>
                <Textarea
                  id="note"
                  value={form.data.note}
                  onChange={(e) => form.setData("note", e.target.value)}
                  rows={4}
                  maxLength={2000}
                />
              </FormField>
            </CardContent>
            <CardFooter className="gap-2 border-t pt-6">
              <Button onClick={() => submit("APPROVED")} disabled={form.processing}>
                {form.processing ? <Loader2 className="animate-spin" /> : <Check />}
                Approve
              </Button>
              <Button variant="destructive" onClick={() => submit("REJECTED")} disabled={form.processing}>
                <X />
                Reject
              </Button>
              <Button variant="outline" asChild>
                <Link href={route("budget_review_queue")}>Back to queue</Link>
              </Button>
            </CardFooter>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Decision</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid gap-4">
                <Detail label="Reviewed by">
                  {request.reviewer ?? "—"}
                  {request.reviewed_at && ` · ${formatRelativeTime(request.reviewed_at)}`}
                </Detail>
                <Detail label="Note">
                  <p className="whitespace-pre-line">{request.review_note || "—"}</p>
                </Detail>
              </dl>
            </CardContent>
            <CardFooter className="border-t pt-6">
              <Button variant="outline" asChild>
                <Link href={route("budget_review_queue", {}, { tab: "history" })}>Back to history</Link>
              </Button>
            </CardFooter>
          </Card>
        )}
      </div>
    </>
  )
}

ReviewShow.layout = (page) => (
  <WorkspaceLayout breadcrumbs={[{ label: "Review queue", route: "budget_review_queue" }, { label: page.props.request.title }]}>
    {page}
  </WorkspaceLayout>
)
