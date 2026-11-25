import { Head } from "@inertiajs/react"
import { Badge } from "@/Components/ui/badge"
import { PageHeader } from "@/Components/admin/PageHeader"
import { WorkspaceLayout } from "@/Layouts/WorkspaceLayout"

export default function WorkspaceHome({ display_name, role, description }) {
  return (
    <>
      <Head title="Workspace" />
      <PageHeader title={`Welcome, ${display_name}`} description={description}>
        <Badge variant="secondary">{role}</Badge>
      </PageHeader>
    </>
  )
}

WorkspaceHome.layout = (page) => <WorkspaceLayout>{page}</WorkspaceLayout>
