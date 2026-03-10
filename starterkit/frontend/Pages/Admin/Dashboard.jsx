import React from "react"
import { Link } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/Components/ui/card"
import { PageHeader } from "@/Components/admin/PageHeader"
import { Users, Shield, ArrowRight } from "lucide-react"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function Dashboard({ stats = { user_count: 0, group_count: 0 } }) {
  return (
    <div className="space-y-8">
      <PageHeader title="Dashboard" />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.user_count}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Groups</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.group_count}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Manage Users</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Create, edit, and manage user accounts and permissions.
            </p>
            <Link href="/admin/users/">
              <Button variant="outline" size="sm">
                View Users
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Manage Groups</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Organize users into groups and assign permissions.
            </p>
            <Link href="/admin/groups/">
              <Button variant="outline" size="sm">
                View Groups
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

Dashboard.layout = AdminLayout
