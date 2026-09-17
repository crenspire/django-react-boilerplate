import { Link } from "@inertiajs/react"
import { Loader2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/Components/ui/card"
import { Input } from "@/Components/ui/input"
import { CheckboxList } from "@/Components/admin/CheckboxList"
import { FormField } from "@/Components/admin/FormField"
import { cn } from "@/lib/utils"

/**
 * Presentational group form shared by the create and edit pages. The page owns
 * the form state (Inertia useForm) and passes it in.
 */
export function GroupForm({
  data,
  setData,
  errors = {},
  permissionsChoices = [],
  canAssignPermissions,
  processing,
  onSubmit,
  cancelHref,
  isNew,
}) {
  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit()
  }

  const selectedCount = data.permission_ids.length

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Group details</CardTitle>
          <CardDescription>Members of a group receive all of its permissions.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-6">
          <FormField label="Name" htmlFor="name" error={errors.name?.[0]} required>
            <Input
              id="name"
              value={data.name}
              onChange={(e) => setData("name", e.target.value)}
              type="text"
              placeholder="e.g. Editors"
              aria-invalid={errors.name?.length ? true : undefined}
              className={cn(errors.name?.length && "border-destructive focus-visible:ring-destructive")}
            />
          </FormField>

          <FormField
            label={`Permissions (${selectedCount} selected)`}
            error={errors.permission_ids?.[0]}
            description={canAssignPermissions ? undefined : "Only superusers can change group permissions."}
          >
            <CheckboxList
              options={permissionsChoices.map((p) => ({ id: p.id, label: p.codename }))}
              selectedIds={data.permission_ids}
              onChange={(ids) => setData("permission_ids", ids)}
              emptyText="No permissions available."
              disabled={!canAssignPermissions}
              labelClassName="font-mono text-xs"
            />
          </FormField>
        </CardContent>
        <CardFooter className="justify-end gap-2 border-t px-6 py-4">
          <Button variant="outline" asChild>
            <Link href={cancelHref}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={processing}>
            {processing && <Loader2 className="animate-spin" />}
            {isNew ? "Create group" : "Save changes"}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
