import * as React from "react"
import { Head, router, useForm } from "@inertiajs/react"
import { Trash2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { DeleteConfirmDialog } from "@/Components/admin/DeleteConfirmDialog"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { GroupForm } from "@/Components/admin/GroupForm"
import { PageHeader } from "@/Components/admin/PageHeader"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function GroupsEdit({ group, form: initialForm, errors = {}, permissions_choices = [], can }) {
  const route = useRoute()
  const form = useForm(initialForm)
  const [deleteOpen, setDeleteOpen] = React.useState(false)
  const [deleting, setDeleting] = React.useState(false)

  const confirmDelete = () => {
    router.post(route("admin_group_delete", { group_id: group.id }), {}, {
      onStart: () => setDeleting(true),
      onFinish: () => {
        setDeleting(false)
        setDeleteOpen(false)
      },
    })
  }

  return (
    <>
      <Head title={group.name} />
      <PageHeader title={group.name} description="Rename the group or change the permissions its members receive.">
        {can.delete && (
          <Button variant="outline" className="text-destructive hover:text-destructive" onClick={() => setDeleteOpen(true)}>
            <Trash2 />
            Delete group
          </Button>
        )}
      </PageHeader>

      <DeleteConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        onConfirm={confirmDelete}
        processing={deleting}
        title="Delete group"
        description={`Are you sure you want to delete "${group.name}"? Members will lose its permissions.`}
      />

      <ErrorSummary errors={errors} className="max-w-3xl" />
      <GroupForm
        data={form.data}
        setData={form.setData}
        errors={errors}
        permissionsChoices={permissions_choices}
        canAssignPermissions={can.assign_permissions}
        processing={form.processing}
        onSubmit={() => form.post(route("admin_group_edit", { group_id: group.id }))}
        cancelHref={route("admin_groups")}
      />
    </>
  )
}

GroupsEdit.layout = (page) => (
  <AdminLayout breadcrumbs={[{ label: "Groups", route: "admin_groups" }, { label: page.props.group.name }]}>
    {page}
  </AdminLayout>
)
