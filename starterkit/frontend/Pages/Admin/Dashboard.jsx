import { Head, Link, usePage } from "@inertiajs/react"
import { ArrowRight, Command, KeyRound, Plus, Shield, ShieldCheck, TrendingUp, UserCheck, Users } from "lucide-react"
import { Avatar, AvatarFallback } from "@/Components/ui/avatar"
import { Badge } from "@/Components/ui/badge"
import { Button } from "@/Components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/Components/ui/card"
import { PageHeader } from "@/Components/admin/PageHeader"
import { RoleBadge, StatusBadge } from "@/Components/admin/UserBadges"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"
import { formatRelativeTime } from "@/lib/date"
import { getDisplayName, getUserInitials } from "@/lib/user"

function percent(part, total) {
  return total ? Math.round((part / total) * 100) : 0
}

function StatCard({ label, value, badge, footerTitle, footerText, icon: Icon }) {
  return (
    <Card className="bg-gradient-to-t from-primary/[0.03] to-card shadow-sm dark:from-primary/[0.06]">
      <CardHeader className="relative space-y-2 pb-3">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-3xl font-semibold tabular-nums">{value}</CardTitle>
        {badge && (
          <Badge variant="outline" className="absolute right-6 top-6">
            {badge}
          </Badge>
        )}
      </CardHeader>
      <CardFooter className="flex-col items-start gap-1 text-sm">
        <div className="flex items-center gap-2 font-medium">
          {footerTitle}
          <Icon className="h-4 w-4" />
        </div>
        <div className="text-muted-foreground">{footerText}</div>
      </CardFooter>
    </Card>
  )
}

export default function Dashboard({ user_stats, group_stats, recent_users, can }) {
  const route = useRoute()
  const { auth } = usePage().props
  const firstName = auth.user?.first_name || auth.user?.username

  const quickActions = [
    can.add_users && { label: "Add a user", description: "Create an account", href: route("admin_user_create"), icon: Plus },
    can.add_groups && { label: "Add a group", description: "Bundle permissions", href: route("admin_group_create"), icon: Plus },
    can.view_users && { label: "Manage users", description: "Search, edit and deactivate", href: route("admin_users"), icon: Users },
    can.view_groups && { label: "Manage groups", description: "Review group permissions", href: route("admin_groups"), icon: Shield },
  ].filter(Boolean)

  return (
    <>
      <Head title="Dashboard" />
      <PageHeader title={`Welcome back, ${firstName}`} description="Here's what's happening across your accounts.">
        {can.add_users && (
          <Button asChild>
            <Link href={route("admin_user_create")}>
              <Plus />
              Add user
            </Link>
          </Button>
        )}
      </PageHeader>

      {(user_stats || group_stats) && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {user_stats && (
            <>
              <StatCard
                label="Total users"
                value={user_stats.total}
                icon={Users}
                footerTitle={`${user_stats.active} active accounts`}
                footerText="All accounts in the system"
              />
              <StatCard
                label="Active users"
                value={user_stats.active}
                badge={
                  <>
                    <TrendingUp />
                    {percent(user_stats.active, user_stats.total)}%
                  </>
                }
                icon={UserCheck}
                footerTitle="Allowed to sign in"
                footerText={`${user_stats.total - user_stats.active} deactivated`}
              />
              <StatCard
                label="Staff members"
                value={user_stats.staff}
                icon={ShieldCheck}
                footerTitle={`${user_stats.superusers} superuser${user_stats.superusers === 1 ? "" : "s"}`}
                footerText="Can access this console"
              />
            </>
          )}
          {group_stats && (
            <StatCard
              label="Groups"
              value={group_stats.total}
              icon={KeyRound}
              footerTitle={`${group_stats.permission_assignments} permissions granted`}
              footerText="Across all groups"
            />
          )}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {can.view_users && (
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-start justify-between space-y-0">
              <div className="space-y-1.5">
                <CardTitle className="text-base">Recent users</CardTitle>
                <CardDescription>The newest accounts to join.</CardDescription>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link href={route("admin_users")}>
                  View all
                  <ArrowRight />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="grid gap-1">
              {recent_users.length === 0 && <p className="py-6 text-center text-sm text-muted-foreground">No users yet.</p>}
              {recent_users.map((user) => {
                const identity = (
                  <>
                    <Avatar className="h-9 w-9">
                      <AvatarFallback className="text-xs font-medium">{getUserInitials(user)}</AvatarFallback>
                    </Avatar>
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium leading-none">{getDisplayName(user)}</p>
                      <p className="mt-1 truncate text-sm text-muted-foreground">{user.email || user.username}</p>
                    </div>
                  </>
                )
                return (
                  <div key={user.id} className="-mx-2 flex items-center gap-4 rounded-md px-2 py-2 hover:bg-muted/50">
                    {user.can_edit ? (
                      <Link href={route("admin_user_edit", { user_id: user.id })} className="flex min-w-0 flex-1 items-center gap-4">
                        {identity}
                      </Link>
                    ) : (
                      <div className="flex min-w-0 flex-1 items-center gap-4">{identity}</div>
                    )}
                    <div className="hidden items-center gap-2 sm:flex">
                      {(user.is_staff || user.is_superuser) && (
                        <RoleBadge isStaff={user.is_staff} isSuperuser={user.is_superuser} />
                      )}
                      {!user.is_active && <StatusBadge active={false} />}
                    </div>
                    <span className="w-24 shrink-0 text-right text-xs text-muted-foreground">
                      {formatRelativeTime(user.date_joined)}
                    </span>
                  </div>
                )
              })}
            </CardContent>
          </Card>
        )}

        <Card className={can.view_users ? "" : "lg:col-span-3"}>
          <CardHeader>
            <CardTitle className="text-base">Quick actions</CardTitle>
            <CardDescription>Common tasks for your role.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2">
            {quickActions.length === 0 && (
              <p className="text-sm text-muted-foreground">
                Your account has no admin permissions yet. Ask a superuser to grant access.
              </p>
            )}
            {quickActions.map((action) => (
              <Link
                key={action.label}
                href={action.href}
                className="group flex items-center gap-3 rounded-lg border p-3 transition-colors hover:bg-muted/50"
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-muted">
                  <action.icon className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{action.label}</p>
                  <p className="text-xs text-muted-foreground">{action.description}</p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
              </Link>
            ))}
          </CardContent>
          <CardFooter className="gap-2 text-xs text-muted-foreground">
            <Command className="h-3.5 w-3.5" />
            Press
            <kbd className="rounded border bg-muted px-1.5 font-mono text-[10px]">⌘K</kbd>
            to jump anywhere
          </CardFooter>
        </Card>
      </div>
    </>
  )
}

Dashboard.layout = (page) => <AdminLayout breadcrumbs={[{ label: "Dashboard" }]}>{page}</AdminLayout>
