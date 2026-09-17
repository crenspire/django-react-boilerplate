import { Link } from "@inertiajs/react"
import { Loader2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/Components/ui/card"
import { Checkbox } from "@/Components/ui/checkbox"
import { Input } from "@/Components/ui/input"
import { CheckboxList } from "@/Components/admin/CheckboxList"
import { FormField } from "@/Components/admin/FormField"
import { cn } from "@/lib/utils"

const FLAGS = [
  {
    name: "is_active",
    label: "Active",
    description: "Inactive accounts cannot sign in.",
    privileged: false,
  },
  {
    name: "is_staff",
    label: "Staff status",
    description: "Can sign in to this admin console.",
    privileged: true,
  },
  {
    name: "is_superuser",
    label: "Superuser",
    description: "Has every permission without assigning them.",
    privileged: true,
  },
]

/**
 * Presentational user form shared by the create and edit pages. The page owns
 * the form state (Inertia useForm) and passes it in.
 */
export function UserForm({
  data,
  setData,
  errors = {},
  groupsChoices = [],
  canGrantPrivileges,
  processing,
  onSubmit,
  cancelHref,
  isNew,
}) {
  const textInput = (name, type = "text", extra = {}) => (
    <Input
      id={name}
      value={data[name]}
      onChange={(e) => setData(name, e.target.value)}
      type={type}
      aria-invalid={errors[name]?.length ? true : undefined}
      className={cn(errors[name]?.length && "border-destructive focus-visible:ring-destructive")}
      {...extra}
    />
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="grid max-w-3xl gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Profile</CardTitle>
          <CardDescription>Sign-in details and how the person appears in the admin.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-5">
          <div className="grid gap-5 sm:grid-cols-2">
            <FormField label="Username" htmlFor="username" error={errors.username?.[0]} required>
              {textInput("username", "text", { autoComplete: "off" })}
            </FormField>
            <FormField
              label="Password"
              htmlFor="password"
              error={errors.password?.join(" ")}
              required={isNew}
              description={isNew ? undefined : "Leave blank to keep the current password."}
            >
              {textInput("password", "password", { autoComplete: "new-password" })}
            </FormField>
          </div>
          <FormField label="Email" htmlFor="email" error={errors.email?.[0]}>
            {textInput("email", "email", { placeholder: "name@example.com" })}
          </FormField>
          <div className="grid gap-5 sm:grid-cols-2">
            <FormField label="First name" htmlFor="first_name" error={errors.first_name?.[0]}>
              {textInput("first_name")}
            </FormField>
            <FormField label="Last name" htmlFor="last_name" error={errors.last_name?.[0]}>
              {textInput("last_name")}
            </FormField>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Access</CardTitle>
          <CardDescription>
            {canGrantPrivileges
              ? "Control whether this account can sign in and what it can manage."
              : "Only superusers can change staff status, superuser status and groups."}
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-6">
          <div className="grid gap-3 sm:grid-cols-3">
            {FLAGS.map(({ name, label, description, privileged }) => {
              const disabled = privileged && !canGrantPrivileges
              return (
                <label
                  key={name}
                  className={cn(
                    "flex items-start gap-3 rounded-lg border p-3 transition-colors has-[[data-state=checked]]:border-primary/40 has-[[data-state=checked]]:bg-muted/50",
                    disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer hover:bg-muted/50",
                    errors[name]?.length && "border-destructive"
                  )}
                >
                  <Checkbox
                    checked={data[name]}
                    onCheckedChange={(v) => setData(name, !!v)}
                    disabled={disabled}
                    className="mt-0.5"
                  />
                  <span className="grid gap-1">
                    <span className="text-sm font-medium leading-none">{label}</span>
                    <span className="text-xs text-muted-foreground">{description}</span>
                    {errors[name]?.length ? (
                      <span className="text-xs font-medium text-destructive">{errors[name][0]}</span>
                    ) : null}
                  </span>
                </label>
              )
            })}
          </div>

          <FormField label="Groups" error={errors.group_ids?.[0]}>
            <CheckboxList
              className="max-h-48"
              options={groupsChoices.map((g) => ({ id: g.id, label: g.name }))}
              selectedIds={data.group_ids}
              onChange={(ids) => setData("group_ids", ids)}
              emptyText="No groups yet."
              disabled={!canGrantPrivileges}
            />
          </FormField>
        </CardContent>
        <CardFooter className="justify-end gap-2 border-t px-6 py-4">
          <Button variant="outline" asChild>
            <Link href={cancelHref}>Cancel</Link>
          </Button>
          <Button type="submit" disabled={processing}>
            {processing && <Loader2 className="animate-spin" />}
            {isNew ? "Create user" : "Save changes"}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
