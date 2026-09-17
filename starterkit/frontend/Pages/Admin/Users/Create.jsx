import { Head, useForm } from "@inertiajs/react"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { PageHeader } from "@/Components/admin/PageHeader"
import { UserForm } from "@/Components/admin/UserForm"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function UsersCreate({ form: initialForm, errors = {}, groups_choices = [], can }) {
  const route = useRoute()
  const form = useForm(initialForm)

  return (
    <>
      <Head title="New user" />
      <PageHeader title="New user" description="Create an account and choose what it can access." />
      <ErrorSummary errors={errors} className="max-w-3xl" />
      <UserForm
        data={form.data}
        setData={form.setData}
        errors={errors}
        groupsChoices={groups_choices}
        canGrantPrivileges={can.grant_privileges}
        processing={form.processing}
        onSubmit={() => form.post(route("admin_user_create"))}
        cancelHref={route("admin_users")}
        isNew
      />
    </>
  )
}

UsersCreate.layout = (page) => (
  <AdminLayout breadcrumbs={[{ label: "Users", route: "admin_users" }, { label: "New user" }]}>{page}</AdminLayout>
)
