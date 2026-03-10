import React from "react"
import { Link, useForm, router } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { Badge } from "@/Components/ui/badge"
import { Card, CardContent } from "@/Components/ui/card"
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/Components/ui/table"
import { Alert, AlertDescription } from "@/Components/ui/alert"
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/Components/ui/dropdown-menu"
import { PageHeader } from "@/Components/admin/PageHeader"
import { SearchBar } from "@/Components/admin/SearchBar"
import { SortableHeader } from "@/Components/admin/SortableHeader"
import { DataTablePagination } from "@/Components/admin/DataTablePagination"
import { DeleteConfirmDialog } from "@/Components/admin/DeleteConfirmDialog"
import { Plus, MoreHorizontal, Pencil, Trash2, AlertCircle } from "lucide-react"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function UsersIndex({
  users = [],
  pagination,
  filters = {},
  errors = {},
}) {
  const searchForm = useForm({
    search: filters?.search ?? "",
  })

  const [deleteTarget, setDeleteTarget] = React.useState(null)

  const currentOrderBy = filters?.order_by ?? "username"

  const doSearch = () => {
    router.get("/admin/users/", {
      search: searchForm.data.search,
      order_by: currentOrderBy,
    }, { preserveState: true })
  }

  const clearSearch = () => {
    router.get("/admin/users/", { order_by: currentOrderBy }, { preserveState: true })
  }

  const onSort = (orderBy) => {
    router.get("/admin/users/", {
      search: filters?.search || "",
      order_by: orderBy,
    }, { preserveState: true })
  }

  const buildPageUrl = (page) => {
    const params = new URLSearchParams()
    if (filters?.search) params.set("search", filters.search)
    if (currentOrderBy) params.set("order_by", currentOrderBy)
    params.set("page", page)
    return `/admin/users/?${params.toString()}`
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Users">
        <Link href="/admin/users/create/">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add user
          </Button>
        </Link>
      </PageHeader>

      {errors?.non_field_errors?.length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {errors.non_field_errors.map((msg, i) => (
              <span key={i}>{msg}</span>
            ))}
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <SearchBar
              value={searchForm.data.search}
              onChange={(v) => searchForm.setData("search", v)}
              onSearch={doSearch}
              onClear={clearSearch}
              placeholder="Search username or email..."
            />

            <div className="overflow-x-auto -mx-1">
              <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>
                    <SortableHeader
                      field="username"
                      currentOrderBy={currentOrderBy}
                      label="Username"
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead>
                    <SortableHeader
                      field="email"
                      currentOrderBy={currentOrderBy}
                      label="Email"
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {!users.length && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                      No users found.
                    </TableCell>
                  </TableRow>
                )}
                {users.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell className="font-medium">
                      <Link
                        href={`/admin/users/${u.id}/edit/`}
                        className="hover:underline"
                      >
                        {u.username}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {u.email || "-"}
                    </TableCell>
                    <TableCell>
                      {u.is_active ? (
                        <Badge
                          variant="outline"
                          className="border-green-200 bg-green-50 text-green-700"
                        >
                          Active
                        </Badge>
                      ) : (
                        <Badge
                          variant="outline"
                          className="border-red-200 bg-red-50 text-red-700"
                        >
                          Inactive
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {u.is_superuser ? (
                          <Badge variant="default">superuser</Badge>
                        ) : u.is_staff ? (
                          <Badge variant="secondary">staff</Badge>
                        ) : null}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon-sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            className="cursor-pointer"
                            onClick={() => router.visit(`/admin/users/${u.id}/edit/`)}
                          >
                            <Pencil className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive cursor-pointer"
                            onClick={() => setDeleteTarget(u)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            </div>

            <DataTablePagination pagination={pagination} buildUrl={buildPageUrl} />

            {deleteTarget && (
              <DeleteConfirmDialog
                open={!!deleteTarget}
                onOpenChange={(v) => !v && setDeleteTarget(null)}
                deleteUrl={`/admin/users/${deleteTarget.id}/delete/`}
                title="Delete user"
                description={`Are you sure you want to delete '${deleteTarget.username}'? This action cannot be undone.`}
              />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

UsersIndex.layout = AdminLayout
