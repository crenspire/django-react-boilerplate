import { Link } from "@inertiajs/react"
import { ArrowLeft, Layers, LockKeyhole, Moon, ServerCog, Sun, Zap } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { useRoute } from "@/composables/useRoute"
import { useTheme } from "@/composables/useTheme"

const HIGHLIGHTS = [
  {
    icon: ServerCog,
    title: "Django stays in charge",
    text: "Authentication, permissions and routing are enforced on the server.",
  },
  {
    icon: Zap,
    title: "Instant navigation",
    text: "Inertia and React give you SPA speed without a separate API.",
  },
  {
    icon: LockKeyhole,
    title: "Least privilege by default",
    text: "Staff only see what their permissions allow.",
  },
]

function Brand({ className = "" }) {
  return (
    <div className={`flex items-center gap-2 font-medium ${className}`}>
      <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
        <Layers className="h-4 w-4" />
      </div>
      Django Inertia
    </div>
  )
}

/** Split-screen authentication shell (shadcn "authentication" example). */
export function AuthLayout({ children }) {
  const route = useRoute()
  const { theme, toggle } = useTheme()

  return (
    <div className="grid min-h-svh lg:grid-cols-2">
      <aside className="relative hidden flex-col overflow-hidden bg-zinc-950 p-10 text-zinc-50 lg:flex dark:border-r dark:border-zinc-800 dark:bg-zinc-900/60">
        {/* Dotted grid fading out toward the bottom */}
        <div
          aria-hidden="true"
          className="absolute inset-0 opacity-40 [background-image:radial-gradient(theme(colors.zinc.700)_1px,transparent_1px)] [background-size:22px_22px] [mask-image:linear-gradient(to_bottom,black,transparent_85%)]"
        />
        <div aria-hidden="true" className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-zinc-500/20 blur-3xl" />

        <Link href={route("home")} className="relative z-10 w-fit">
          <div className="flex items-center gap-2 text-lg font-medium">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-zinc-50 text-zinc-950">
              <Layers className="h-4 w-4" />
            </div>
            Django Inertia
          </div>
        </Link>

        <div className="relative z-10 mt-auto space-y-8">
          <div className="space-y-2">
            <h2 className="text-3xl font-semibold tracking-tight">Admin console</h2>
            <p className="max-w-md text-zinc-400">
              Manage users, groups and permissions for your application from one place.
            </p>
          </div>
          <ul className="grid gap-5">
            {HIGHLIGHTS.map(({ icon: Icon, title, text }) => (
              <li key={title} className="flex gap-4">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900">
                  <Icon className="h-4 w-4 text-zinc-300" />
                </div>
                <div>
                  <p className="font-medium">{title}</p>
                  <p className="text-sm text-zinc-400">{text}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <main className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex items-center justify-between">
          <Brand className="lg:invisible" />
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="sm" asChild>
              <Link href={route("home")}>
                <ArrowLeft />
                Back to site
              </Link>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggle}
              aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {theme === "dark" ? <Sun /> : <Moon />}
            </Button>
          </div>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-sm">{children}</div>
        </div>
        <p className="text-center text-xs text-muted-foreground">
          Protected area. Sign-in attempts are rate limited.
        </p>
      </main>
    </div>
  )
}
