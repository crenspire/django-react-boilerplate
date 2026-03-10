import React from "react"
import { useForm } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { Input } from "@/Components/ui/input"
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/Components/ui/card"
import { Alert, AlertDescription } from "@/Components/ui/alert"
import { FormField } from "@/Components/admin/FormField"
import { AlertCircle } from "lucide-react"
import { AuthLayout } from "@/Layouts/AuthLayout"

export default function Login({ form: formInitial = {}, errors = {} }) {
  const loginForm = useForm({
    username: formInitial?.username ?? "",
    password: formInitial?.password ?? "",
    next: formInitial?.next ?? "/admin/",
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    loginForm.post("/admin/login/")
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sign in</CardTitle>
        <CardDescription>
          Enter your credentials to access the admin panel
        </CardDescription>
      </CardHeader>
      <CardContent>
        {errors?.non_field_errors?.length > 0 && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {errors.non_field_errors.map((msg, i) => (
                <span key={i}>{msg}</span>
              ))}
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="hidden" name="next" value={loginForm.data.next} />

          <FormField
            label="Username"
            htmlFor="username"
            error={errors?.username?.[0]}
          >
            <Input
              id="username"
              value={loginForm.data.username}
              onChange={(e) => loginForm.setData("username", e.target.value)}
              type="text"
              autoComplete="username"
              placeholder="Enter your username"
              className={errors?.username?.length ? "border-destructive" : ""}
            />
          </FormField>

          <FormField
            label="Password"
            htmlFor="password"
            error={errors?.password?.[0]}
          >
            <Input
              id="password"
              value={loginForm.data.password}
              onChange={(e) => loginForm.setData("password", e.target.value)}
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              className={errors?.password?.length ? "border-destructive" : ""}
            />
          </FormField>

          <Button type="submit" className="w-full" disabled={loginForm.processing}>
            Sign in
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}

Login.layout = AuthLayout
