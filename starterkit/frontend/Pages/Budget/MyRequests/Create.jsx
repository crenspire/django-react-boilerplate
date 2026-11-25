import { Head, useForm } from "@inertiajs/react"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { PageHeader } from "@/Components/admin/PageHeader"
import { BudgetRequestForm } from "@/Components/budget/BudgetRequestForm"
import { useRoute } from "@/composables/useRoute"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"

export default function MyRequestsCreate({ form: initialForm, errors = {} }) {
  const route = useRoute()
  const form = useForm(initialForm)

  return (
    <>
      <Head title="New request" />
      <PageHeader title="New budget request" description="Submit a funding request for review." />
      <ErrorSummary errors={errors} className="max-w-2xl" />
      <BudgetRequestForm
        data={form.data}
        setData={form.setData}
        errors={errors}
        processing={form.processing}
        onSubmit={() => form.post(route("budget_request_create"))}
        cancelHref={route("budget_my_requests")}
        submitLabel="Submit request"
      />
    </>
  )
}

MyRequestsCreate.layout = (page) => (
  <WorkspaceLayout breadcrumbs={[{ label: "My requests", route: "budget_my_requests" }, { label: "New" }]}>
    {page}
  </WorkspaceLayout>
)
