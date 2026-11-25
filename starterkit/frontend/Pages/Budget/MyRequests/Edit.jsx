import { Head, useForm } from "@inertiajs/react"
import { Lock } from "lucide-react"
import { Alert, AlertDescription } from "@/Components/ui/alert"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { PageHeader } from "@/Components/admin/PageHeader"
import { BudgetRequestForm } from "@/Components/budget/BudgetRequestForm"
import { StatusBadge } from "@/Components/budget/StatusBadge"
import { useRoute } from "@/composables/useRoute"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"

export default function MyRequestsEdit({ request, form: initialForm, errors = {}, editable, locked_message }) {
  const route = useRoute()
  const form = useForm(initialForm)

  return (
    <>
      <Head title={request.title} />
      <PageHeader title={request.title} description="Update your request while it is pending.">
        <StatusBadge status={request.status} label={request.status_label} />
      </PageHeader>
      {locked_message && (
        <Alert className="max-w-2xl">
          <Lock className="h-4 w-4" />
          <AlertDescription>{locked_message}</AlertDescription>
        </Alert>
      )}
      <ErrorSummary errors={errors} className="max-w-2xl" />
      <BudgetRequestForm
        data={form.data}
        setData={form.setData}
        errors={errors}
        processing={form.processing}
        disabled={!editable}
        onSubmit={() => form.post(route("budget_request_edit", { request_id: request.id }))}
        cancelHref={route("budget_my_requests")}
        submitLabel="Save changes"
      />
    </>
  )
}

MyRequestsEdit.layout = (page) => (
  <WorkspaceLayout breadcrumbs={[{ label: "My requests", route: "budget_my_requests" }, { label: page.props.request.title }]}>
    {page}
  </WorkspaceLayout>
)
