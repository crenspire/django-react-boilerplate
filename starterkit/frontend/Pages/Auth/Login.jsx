import * as React from "react"
import { Head, useForm, usePage } from "@inertiajs/react"
import { Eye, EyeOff, Loader2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Input } from "@/Components/ui/input"
import { ErrorSummary } from "@/Components/admin/ErrorSummary"
import { FlashMessages } from "@/Components/admin/FlashMessages"
import { FormField } from "@/Components/admin/FormField"
import { useRoute } from "@/composables/useRoute"
import { AuthLayout } from "@/Layouts/AuthLayout"
import { cn } from "@/lib/utils"

export default function Login({ form: initialForm, errors = {} }) {
  const route = useRoute()
  const { flash } = usePage().props
  const loginForm = useForm(initialForm)
  const [showPassword, setShowPassword] = React.useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    loginForm.post(route("login"), {
      onFinish: () => loginForm.setData("password", ""),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <Head title="Sign in" />
      <div className="flex flex-col gap-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
        <p className="text-balance text-sm text-muted-foreground">
          Sign in with your staff account to continue
        </p>
      </div>

      <FlashMessages messages={flash} />
      <ErrorSummary errors={{ non_field_errors: errors.non_field_errors ?? [] }} />

      <div className="grid gap-5">
        <FormField label="Username" htmlFor="username" error={errors.username?.[0]}>
          <Input
            id="username"
            value={loginForm.data.username}
            onChange={(e) => loginForm.setData("username", e.target.value)}
            type="text"
            autoComplete="username"
            autoFocus
            placeholder="admin"
            aria-invalid={errors.username?.length ? true : undefined}
            className={cn(errors.username?.length && "border-destructive focus-visible:ring-destructive")}
          />
        </FormField>

        <FormField label="Password" htmlFor="password" error={errors.password?.[0]}>
          <div className="relative">
            <Input
              id="password"
              value={loginForm.data.password}
              onChange={(e) => loginForm.setData("password", e.target.value)}
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              aria-invalid={errors.password?.length ? true : undefined}
              className={cn("pr-10", errors.password?.length && "border-destructive focus-visible:ring-destructive")}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute right-0.5 top-1/2 h-8 w-8 -translate-y-1/2 text-muted-foreground hover:bg-transparent"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label={showPassword ? "Hide password" : "Show password"}
              aria-pressed={showPassword}
            >
              {showPassword ? <EyeOff /> : <Eye />}
            </Button>
          </div>
        </FormField>

        <Button type="submit" className="w-full" disabled={loginForm.processing}>
          {loginForm.processing && <Loader2 className="animate-spin" />}
          Sign in
        </Button>
      </div>

      <p className="text-center text-sm text-muted-foreground">
        Need access? Ask an administrator to create an account for you.
      </p>
    </form>
  )
}

Login.layout = (page) => <AuthLayout>{page}</AuthLayout>
