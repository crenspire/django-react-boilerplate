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

export default function GroupsIndex({
  groups = [],
  pagination,
  filters = {},
  errors = {},
}) {
  const searchForm = useForm({
    search: filters?.search ?? "",
  })

  const [deleteTarget, setDeleteTarget] = React.useState(null)

  const currentOrderBy = filters?.order_by ?? "name"

  const doSearch = () => {
    router.get("/admin/groups/", {
      search: searchForm.data.search,
      order_by: currentOrderBy,
    }, { preserveState: true })
  }

  const clearSearch = () => {
    router.get("/admin/groups/", { order_by: currentOrderBy }, { preserveState: true })
  }

  const onSort = (orderBy) => {
    router.get("/admin/groups/", {
      search: filters?.search || "",
      order_by: orderBy,
    }, { preserveState: true })
  }

  const buildPageUrl = (page) => {
    const params = new URLSearchParams()
    if (filters?.search) params.set("search", filters.search)
    if (currentOrderBy) params.set("order_by", currentOrderBy)
    params.set("page", page)
    return `/admin/groups/?${params.toString()}`
  }

  return (
    <div className="space-y-6">
      <PageHeader title="Groups">
        <Link href="/admin/groups/create/">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add group
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
              placeholder="Search group name..."
            />

            <div className="overflow-x-auto -mx-1">
              <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>
                    <SortableHeader
                      field="name"
                      currentOrderBy={currentOrderBy}
                      label="Name"
                      onSort={onSort}
                    />
                  </TableHead>
                  <TableHead>Users</TableHead>
                  <TableHead>Permissions</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {!groups.length && (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center text-muted-foreground py-8">
                      No groups found.
                    </TableCell>
                  </TableRow>
                )}
                {groups.map((g) => (
                  <TableRow key={g.id}>
                    <TableCell className="font-medium">
                      <Link
                        href={`/admin/groups/${g.id}/edit/`}
                        className="hover:underline"
                      >
                        {g.name}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{g.user_count}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{g.permission_count}</Badge>
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
                            onClick={() => router.visit(`/admin/groups/${g.id}/edit/`)}
                          >
                            <Pencil className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive cursor-pointer"
                            onClick={() => setDeleteTarget(g)}
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
                deleteUrl={`/admin/groups/${deleteTarget.id}/delete/`}
                title="Delete group"
                description={`Are you sure you want to delete '${deleteTarget.name}'? This action cannot be undone.`}
              />
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

GroupsIndex.layout = AdminLayout
