import React from "react"
import { Link, useForm } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { Input } from "@/Components/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "@/Components/ui/card"
import { Checkbox } from "@/Components/ui/checkbox"
import { Separator } from "@/Components/ui/separator"
import { Alert, AlertDescription } from "@/Components/ui/alert"
import { FormField } from "@/Components/admin/FormField"
import { PageHeader } from "@/Components/admin/PageHeader"
import { AlertCircle } from "lucide-react"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function UsersCreate({
  form: formInitial = {},
  errors = {},
  groups_choices = [],
}) {
  const form = useForm({
    username: formInitial?.username ?? "",
    email: formInitial?.email ?? "",
    first_name: formInitial?.first_name ?? "",
    last_name: formInitial?.last_name ?? "",
    is_staff: formInitial?.is_staff ?? false,
    is_superuser: formInitial?.is_superuser ?? false,
    is_active: formInitial?.is_active ?? true,
    group_ids: formInitial?.group_ids ?? [],
    password: formInitial?.password ?? "",
  })

  const toggleGroup = (id) => {
    const prev = form.data.group_ids
    const idx = prev.indexOf(id)
    if (idx > -1) {
      form.setData(
        "group_ids",
        prev.filter((x) => x !== id)
      )
    } else {
      form.setData("group_ids", [...prev, id])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    form.post("/admin/users/create/")
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Add user"
        breadcrumbs={[{ label: "Users", href: "/admin/users/" }]}
      />

      {Object.keys(errors).length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <ul className="list-disc list-inside">
              {Object.entries(errors).map(([key, msgs]) => (
                <li key={key}>
                  {key}: {Array.isArray(msgs) ? msgs[0] : msgs}
                </li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="text-lg">User details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <FormField
                label="Username"
                htmlFor="username"
                error={errors?.username?.[0]}
                required
              >
                <Input
                  id="username"
                  value={form.data.username}
                  onChange={(e) => form.setData("username", e.target.value)}
                  type="text"
                  className={errors?.username?.length ? "border-destructive" : ""}
                />
              </FormField>
              <FormField
                label="Password"
                htmlFor="password"
                error={errors?.password?.[0]}
                required
              >
                <Input
                  id="password"
                  value={form.data.password}
                  onChange={(e) => form.setData("password", e.target.value)}
                  type="password"
                  className={errors?.password?.length ? "border-destructive" : ""}
                />
              </FormField>
            </div>

            <FormField label="Email" htmlFor="email">
              <Input
                id="email"
                value={form.data.email}
                onChange={(e) => form.setData("email", e.target.value)}
                type="email"
              />
            </FormField>

            <div className="grid grid-cols-2 gap-4">
              <FormField label="First name" htmlFor="first_name">
                <Input
                  id="first_name"
                  value={form.data.first_name}
                  onChange={(e) => form.setData("first_name", e.target.value)}
                  type="text"
                />
              </FormField>
              <FormField label="Last name" htmlFor="last_name">
                <Input
                  id="last_name"
                  value={form.data.last_name}
                  onChange={(e) => form.setData("last_name", e.target.value)}
                  type="text"
                />
              </FormField>
            </div>

            <Separator />

            <div className="space-y-3">
              <p className="text-sm font-medium">Permissions</p>
              <div className="flex flex-wrap gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={form.data.is_staff}
                    onCheckedChange={(v) => form.setData("is_staff", !!v)}
                  />
                  <span className="text-sm">Staff status</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={form.data.is_superuser}
                    onCheckedChange={(v) => form.setData("is_superuser", !!v)}
                  />
                  <span className="text-sm">Superuser</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <Checkbox
                    checked={form.data.is_active}
                    onCheckedChange={(v) => form.setData("is_active", !!v)}
                  />
                  <span className="text-sm">Active</span>
                </label>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <p className="text-sm font-medium">Groups</p>
              <Card className="max-h-48 overflow-y-auto">
                <CardContent className="p-3 space-y-2">
                  {!groups_choices.length ? (
                    <p className="text-sm text-muted-foreground">No groups available.</p>
                  ) : (
                    groups_choices.map((g) => (
                      <label key={g.id} className="flex items-center gap-2 cursor-pointer">
                        <Checkbox
                          checked={form.data.group_ids.includes(g.id)}
                          onCheckedChange={() => toggleGroup(g.id)}
                        />
                        <span className="text-sm">{g.name}</span>
                      </label>
                    ))
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="flex gap-2 pt-2">
              <Button type="submit" disabled={form.processing}>
                Save
              </Button>
              <Link href="/admin/users/">
                <Button variant="outline" type="button">
                  Cancel
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

UsersCreate.layout = AdminLayout
