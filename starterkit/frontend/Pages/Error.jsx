import { Head, Link, usePage } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import { useRoute } from "@/composables/useRoute"

export default function Error({ status, title, message }) {
  const route = useRoute()
  const { auth } = usePage().props

  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-6 bg-background p-6 text-center">
      <Head title={title} />
      <div className="space-y-2">
        <p className="text-sm font-medium text-muted-foreground">{status}</p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">{title}</h1>
        <p className="max-w-md text-muted-foreground">{message}</p>
      </div>
      <Button asChild>
        {auth?.user ? <Link href={route("workspace")}>Back to workspace</Link> : <Link href={route("home")}>Back to home</Link>}
      </Button>
    </main>
  )
}
