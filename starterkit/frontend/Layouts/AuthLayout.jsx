import * as React from "react"

export function AuthLayout({ children }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="w-full max-w-md px-4">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-foreground">Admin Panel</h1>
          <p className="text-sm text-muted-foreground mt-1">Sign in to manage your application</p>
        </div>
        {children}
      </div>
    </div>
  )
}
