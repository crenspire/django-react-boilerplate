import * as React from "react"
import { Head, Link, router } from "@inertiajs/react"
import { KeyRound, MoreHorizontal, Pencil, Plus, Shield, ShieldOff, Trash2, Users } from "lucide-react"
import { Badge } from "@/Components/ui/badge"
import { Button } from "@/Components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/Components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/Components/ui/table"
import { DataTablePagination } from "@/Components/admin/DataTablePagination"
import { DeleteConfirmDialog } from "@/Components/admin/DeleteConfirmDialog"
import { PageHeader } from "@/Components/admin/PageHeader"
import { SearchBar } from "@/Components/admin/SearchBar"
import { SortableHeader } from "@/Components/admin/SortableHeader"
import { useListFilters } from "@/composables/useListFilters"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"

export default function GroupsIndex({ groups, pagination, filters, can }) {
  const route = useRoute()
  const { search, setSearch, sortBy, pageUrl } = useListFilters("admin_groups", filters)
  const [deleteTarget, setDeleteTarget] = React.useState(null)
  const [deleting, setDeleting] = React.useState(false)

  const confirmDelete = () => {
    router.post(route("admin_group_delete", { group_id: deleteTarget.id }), {}, {
      onStart: () => setDeleting(true),
      onFinish: () => {
        setDeleting(false)
        setDeleteTarget(null)
      },
    })
  }

  const sortHeader = (field, label) => (
    <SortableHeader field={field} currentOrderBy={filters.order_by} label={label} onSort={sortBy} />
  )

  return (
    <>
      <Head title="Groups" />
      <PageHeader title="Groups" description="Bundle permissions and grant them to many users at once.">
        {can.add && (
          <Button asChild>
            <Link href={route("admin_group_create")}>
              <Plus />
              Add group
            </Link>
          </Button>
        )}
      </PageHeader>

      <div className="flex flex-col gap-4">
        <SearchBar value={search} onChange={setSearch} placeholder="Filter groups…" />

        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow className="hover:bg-transparent">
                <TableHead>{sortHeader("name", "Name")}</TableHead>
                <TableHead>{sortHeader("user_count", "Members")}</TableHead>
                <TableHead>{sortHeader("permission_count", "Permissions")}</TableHead>
                <TableHead className="w-12">
                  <span className="sr-only">Actions</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!groups.length && (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={4} className="h-40">
                    <div className="flex flex-col items-center gap-2 text-center">
                      <ShieldOff className="h-8 w-8 text-muted-foreground" />
                      <p className="font-medium">No groups found</p>
                      <p className="text-sm text-muted-foreground">
                        {filters.search ? "Try a different search term." : "Create a group to share permissions."}
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
              {groups.map((g) => (
                <TableRow key={g.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <div className="flex h-8 w-8 items-center justify-center rounded-md border bg-muted/50">
                        <Shield className="h-4 w-4 text-muted-foreground" />
                      </div>
                      {g.can_edit ? (
                        <Link
                          href={route("admin_group_edit", { group_id: g.id })}
                          className="font-medium underline-offset-4 hover:underline"
                        >
                          {g.name}
                        </Link>
                      ) : (
                        <span className="font-medium">{g.name}</span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-muted-foreground">
                      <Users />
                      {g.user_count}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-muted-foreground">
                      <KeyRound />
                      {g.permission_count}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    {(g.can_edit || g.can_delete) && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 data-[state=open]:bg-muted" aria-label={`Actions for ${g.name}`}>
                            <MoreHorizontal />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-40">
                          {g.can_edit && (
                            <DropdownMenuItem className="gap-2" onSelect={() => router.visit(route("admin_group_edit", { group_id: g.id }))}>
                              <Pencil className="h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                          )}
                          {g.can_edit && g.can_delete && <DropdownMenuSeparator />}
                          {g.can_delete && (
                            <DropdownMenuItem
                              className="gap-2 text-destructive focus:text-destructive"
                              onSelect={() => setDeleteTarget(g)}
                            >
                              <Trash2 className="h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <DataTablePagination pagination={pagination} buildUrl={pageUrl} itemLabel="groups" />
      </div>

      <DeleteConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        onConfirm={confirmDelete}
        processing={deleting}
        title="Delete group"
        description={`Are you sure you want to delete "${deleteTarget?.name}"? Members will lose its permissions.`}
      />
    </>
  )
}

GroupsIndex.layout = (page) => <AdminLayout breadcrumbs={[{ label: "Groups" }]}>{page}</AdminLayout>
