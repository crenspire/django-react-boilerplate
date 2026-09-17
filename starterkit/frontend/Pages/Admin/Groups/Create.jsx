import { Head, useForm } from "@inertiajs/react"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { GroupForm } from "@/Components/admin/GroupForm"
import { PageHeader } from "@/Components/admin/PageHeader"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function GroupsCreate({ form: initialForm, errors = {}, permissions_choices = [], can }) {
  const route = useRoute()
  const form = useForm(initialForm)

  return (
    <>
      <Head title="New group" />
      <PageHeader title="New group" description="Name the group and pick the permissions its members get." />
      <ErrorSummary errors={errors} className="max-w-3xl" />
      <GroupForm
        data={form.data}
        setData={form.setData}
        errors={errors}
        permissionsChoices={permissions_choices}
        canAssignPermissions={can.assign_permissions}
        processing={form.processing}
        onSubmit={() => form.post(route("admin_group_create"))}
        cancelHref={route("admin_groups")}
        isNew
      />
    </>
  )
}

GroupsCreate.layout = (page) => (
  <AdminLayout breadcrumbs={[{ label: "Groups", route: "admin_groups" }, { label: "New group" }]}>{page}</AdminLayout>
)
