import * as React from "react"
import { Head, Link, router } from "@inertiajs/react"
import { MoreHorizontal, Pencil, Plus, Trash2, UserX } from "lucide-react"
import { Avatar, AvatarFallback } from "@/Components/ui/avatar"
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
import { RoleBadge, StatusBadge } from "@/Components/admin/UserBadges"
import { useListFilters } from "@/composables/useListFilters"
import { useRoute } from "@/composables/useRoute"
import { AdminLayout } from "@/Layouts/AdminLayout"
import { getDisplayName, getUserInitials } from "@/lib/user"

export default function UsersIndex({ users, pagination, filters, can }) {
  const route = useRoute()
  const { search, setSearch, sortBy, pageUrl } = useListFilters("admin_users", filters)
  const [deleteTarget, setDeleteTarget] = React.useState(null)
  const [deleting, setDeleting] = React.useState(false)

  const confirmDelete = () => {
    router.post(route("admin_user_delete", { user_id: deleteTarget.id }), {}, {
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
      <Head title="Users" />
      <PageHeader title="Users" description="Manage accounts, roles and who can sign in.">
        {can.add && (
          <Button asChild>
            <Link href={route("admin_user_create")}>
              <Plus />
              Add user
            </Link>
          </Button>
        )}
      </PageHeader>

      <div className="flex flex-col gap-4">
        <SearchBar value={search} onChange={setSearch} placeholder="Filter by username or email…" />

        <div className="overflow-hidden rounded-lg border">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow className="hover:bg-transparent">
                <TableHead>{sortHeader("username", "User")}</TableHead>
                <TableHead className="hidden md:table-cell">{sortHeader("email", "Email")}</TableHead>
                <TableHead>{sortHeader("is_active", "Status")}</TableHead>
                <TableHead className="hidden sm:table-cell">{sortHeader("is_staff", "Role")}</TableHead>
                <TableHead className="w-12">
                  <span className="sr-only">Actions</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {!users.length && (
                <TableRow className="hover:bg-transparent">
                  <TableCell colSpan={5} className="h-40">
                    <div className="flex flex-col items-center gap-2 text-center">
                      <UserX className="h-8 w-8 text-muted-foreground" />
                      <p className="font-medium">No users found</p>
                      <p className="text-sm text-muted-foreground">
                        {filters.search ? "Try a different search term." : "Create the first account to get started."}
                      </p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
              {users.map((u) => (
                <TableRow key={u.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="text-xs font-medium">{getUserInitials(u)}</AvatarFallback>
                      </Avatar>
                      <div className="min-w-0">
                        {u.can_edit ? (
                          <Link
                            href={route("admin_user_edit", { user_id: u.id })}
                            className="font-medium underline-offset-4 hover:underline"
                          >
                            {getDisplayName(u)}
                          </Link>
                        ) : (
                          <span className="font-medium">{getDisplayName(u)}</span>
                        )}
                        <p className="truncate text-xs text-muted-foreground">@{u.username}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="hidden text-muted-foreground md:table-cell">{u.email || "—"}</TableCell>
                  <TableCell>
                    <StatusBadge active={u.is_active} />
                  </TableCell>
                  <TableCell className="hidden sm:table-cell">
                    <RoleBadge isStaff={u.is_staff} isSuperuser={u.is_superuser} />
                  </TableCell>
                  <TableCell className="text-right">
                    {(u.can_edit || u.can_delete) && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 data-[state=open]:bg-muted" aria-label={`Actions for ${u.username}`}>
                            <MoreHorizontal />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-40">
                          {u.can_edit && (
                            <DropdownMenuItem className="gap-2" onSelect={() => router.visit(route("admin_user_edit", { user_id: u.id }))}>
                              <Pencil className="h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                          )}
                          {u.can_edit && u.can_delete && <DropdownMenuSeparator />}
                          {u.can_delete && (
                            <DropdownMenuItem
                              className="gap-2 text-destructive focus:text-destructive"
                              onSelect={() => setDeleteTarget(u)}
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

        <DataTablePagination pagination={pagination} buildUrl={pageUrl} itemLabel="users" />
      </div>

      <DeleteConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        onConfirm={confirmDelete}
        processing={deleting}
        title="Delete user"
        description={`Are you sure you want to delete "${deleteTarget?.username}"? This action cannot be undone.`}
      />
    </>
  )
}

UsersIndex.layout = (page) => <AdminLayout breadcrumbs={[{ label: "Users" }]}>{page}</AdminLayout>
