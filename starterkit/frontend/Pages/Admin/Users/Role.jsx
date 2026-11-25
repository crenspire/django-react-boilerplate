import { Head, Link, useForm } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/Components/ui/select"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { FormField } from "@/Components/admin/FormField"
import { PageHeader } from "@/Components/admin/PageHeader"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function UsersRole({ user, form: initialForm, errors = {}, role_choices, fixed_role_message }) {
  const route = useRoute()
  const form = useForm(initialForm)

  const handleSubmit = (e) => {
    e.preventDefault()
    form.post(route("admin_user_role", { user_id: user.id }))
  }

  return (
    <>
      <Head title={`Role for ${user.username}`} />
      <PageHeader title={user.username} description="Choose what this account can do with budget requests." />

      <ErrorSummary errors={errors} className="max-w-md" />
      <form onSubmit={handleSubmit} className="flex max-w-md flex-col gap-6">
        <FormField label="Role" htmlFor="role" error={errors.role?.[0]} description={fixed_role_message}>
          <Select
            value={form.data.role}
            onValueChange={(value) => form.setData("role", value)}
            disabled={!!fixed_role_message}
          >
            <SelectTrigger id="role">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {role_choices.map((choice) => (
                <SelectItem key={choice.value} value={choice.value}>
                  {choice.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </FormField>

        <div className="flex gap-2">
          <Button type="submit" disabled={form.processing || !!fixed_role_message}>
            Save role
          </Button>
          <Button variant="outline" asChild>
            <Link href={route("admin_users")}>Cancel</Link>
          </Button>
        </div>
      </form>
    </>
  )
}

UsersRole.layout = (page) => (
  <AdminLayout breadcrumbs={[{ label: "Users", route: "admin_users" }, { label: `${page.props.user.username} – role` }]}>
    {page}
  </AdminLayout>
)
