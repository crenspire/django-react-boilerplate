import React from "react"
import { Link, useForm } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { Input } from "@/Components/ui/input"
import { Card, CardHeader, CardTitle, CardContent } from "@/Components/ui/card"
import { Checkbox } from "@/Components/ui/checkbox"
import { Alert, AlertDescription } from "@/Components/ui/alert"
import { FormField } from "@/Components/admin/FormField"
import { PageHeader } from "@/Components/admin/PageHeader"
import { AlertCircle } from "lucide-react"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function GroupsCreate({
  form: formInitial = {},
  errors = {},
  permissions_choices = [],
}) {
  const form = useForm({
    name: formInitial?.name ?? "",
    permission_ids: Array.isArray(formInitial?.permission_ids)
      ? [...formInitial.permission_ids]
      : [],
  })

  const togglePermission = (id) => {
    const prev = form.data.permission_ids
    const idx = prev.indexOf(id)
    if (idx > -1) {
      form.setData(
        "permission_ids",
        prev.filter((x) => x !== id)
      )
    } else {
      form.setData("permission_ids", [...prev, id])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    form.post("/admin/groups/create/")
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Add group"
        breadcrumbs={[{ label: "Groups", href: "/admin/groups/" }]}
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
          <CardTitle className="text-lg">Group details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <FormField
              label="Name"
              htmlFor="name"
              error={errors?.name?.[0]}
              required
            >
              <Input
                id="name"
                value={form.data.name}
                onChange={(e) => form.setData("name", e.target.value)}
                type="text"
                className={errors?.name?.length ? "border-destructive" : ""}
              />
            </FormField>

            <div className="space-y-3">
              <p className="text-sm font-medium">Permissions</p>
              <Card className="max-h-60 overflow-y-auto">
                <CardContent className="p-3 space-y-2">
                  {!permissions_choices.length ? (
                    <p className="text-sm text-muted-foreground">No permissions available.</p>
                  ) : (
                    permissions_choices.map((p) => (
                      <label key={p.id} className="flex items-center gap-2 cursor-pointer">
                        <Checkbox
                          checked={form.data.permission_ids.includes(p.id)}
                          onCheckedChange={() => togglePermission(p.id)}
                        />
                        <span className="text-sm font-mono">{p.codename}</span>
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
              <Link href="/admin/groups/">
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

GroupsCreate.layout = AdminLayout
