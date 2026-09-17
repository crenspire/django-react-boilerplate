import * as React from "react"
import { Head, router, useForm } from "@inertiajs/react"
import { Trash2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { DeleteConfirmDialog } from "@/Components/admin/DeleteConfirmDialog"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { PageHeader } from "@/Components/admin/PageHeader"
import { UserForm } from "@/Components/admin/UserForm"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function UsersEdit({ user, form: initialForm, errors = {}, groups_choices = [], can }) {
  const route = useRoute()
  const form = useForm(initialForm)
  const [deleteOpen, setDeleteOpen] = React.useState(false)
  const [deleting, setDeleting] = React.useState(false)

  const confirmDelete = () => {
    router.post(route("admin_user_delete", { user_id: user.id }), {}, {
      onStart: () => setDeleting(true),
      onFinish: () => {
        setDeleting(false)
        setDeleteOpen(false)
      },
    })
  }

  return (
    <>
      <Head title={user.username} />
      <PageHeader title={user.username} description="Update profile details and access for this account.">
        {can.delete && (
          <Button variant="outline" className="text-destructive hover:text-destructive" onClick={() => setDeleteOpen(true)}>
            <Trash2 />
            Delete user
          </Button>
        )}
      </PageHeader>

      <DeleteConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        onConfirm={confirmDelete}
        processing={deleting}
        title="Delete user"
        description={`Are you sure you want to delete "${user.username}"? This action cannot be undone.`}
      />

      <ErrorSummary errors={errors} className="max-w-3xl" />
      <UserForm
        data={form.data}
        setData={form.setData}
        errors={errors}
        groupsChoices={groups_choices}
        canGrantPrivileges={can.grant_privileges}
        processing={form.processing}
        onSubmit={() => form.post(route("admin_user_edit", { user_id: user.id }))}
        cancelHref={route("admin_users")}
      />
    </>
  )
}

UsersEdit.layout = (page) => (
  <AdminLayout breadcrumbs={[{ label: "Users", route: "admin_users" }, { label: page.props.user.username }]}>
    {page}
  </AdminLayout>
)
