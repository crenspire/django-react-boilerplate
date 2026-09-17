import { Head, Link, usePage } from "@inertiajs/react"
import { Button } from "@/Components/ui/button"
import {
  Zap,
  Layers,
  Palette,
  Shield,
  ArrowRight,
  Github,
  BookOpen,
  Sun,
  Moon,
} from "lucide-react"
import { useRoute } from "@/composables/useRoute"
import { useTheme } from "@/composables/useTheme"

const FEATURES = [
  {
    title: "Django 6",
    description:
      "Backend, auth, and ORM. One server, no separate API to maintain.",
    icon: Zap,
    iconBg: "from-emerald-500/20 to-teal-500/20 border-emerald-500/30",
    iconColor: "text-emerald-600 dark:text-emerald-400",
  },
  {
    title: "Inertia.js",
    description:
      "SPA feel with server-side routing. Shared auth and no token juggling.",
    icon: Layers,
    iconBg: "from-violet-500/20 to-purple-500/20 border-violet-500/30",
    iconColor: "text-violet-600 dark:text-violet-400",
  },
  {
    title: "React + shadcn-ui",
    description:
      "Vite, and accessible, customizable UI components.",
    icon: Palette,
    iconBg: "from-amber-500/20 to-orange-500/20 border-amber-500/30",
    iconColor: "text-amber-600 dark:text-amber-400",
  },
  {
    title: "Admin panel",
    description:
      "User & group CRUD with Inertia/React plus classic Django admin.",
    icon: Shield,
    iconBg: "from-blue-500/20 to-indigo-500/20 border-blue-500/30",
    iconColor: "text-blue-600 dark:text-blue-400",
  },
]

export default function Home() {
  const { theme, toggle: toggleTheme } = useTheme()
  const page = usePage()
  const route = useRoute()
  const isSignedIn = !!page.props.auth?.user
  const adminHref = isSignedIn ? route("admin_dashboard") : route("login")

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Head title="Home" />
      <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/80 backdrop-blur-xl shadow-sm shadow-black/5">
        <div className="container flex h-16 max-w-5xl mx-auto items-center justify-between px-4">
          <Link
            href={route("home")}
            className="flex items-center font-semibold text-foreground tracking-tight hover:opacity-90 transition-opacity"
          >
            <span className="text-xl bg-gradient-to-r from-violet-600 to-indigo-600 dark:from-violet-400 dark:to-indigo-400 bg-clip-text text-transparent font-bold">
              Django Inertia React
            </span>
          </Link>
          <nav className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 shrink-0"
              aria-label="Toggle dark mode"
              onClick={toggleTheme}
            >
              {theme === "light" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          
            <Button
              size="sm"
              asChild
              className="gap-1.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white border-0 shadow-md shadow-violet-500/25"
            >
              <Link href={adminHref}>
                {isSignedIn ? "Admin" : "Get started"}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </nav>
        </div>
      </header>

      <section className="relative flex-1 overflow-hidden py-24 md:py-32">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-violet-400/20 dark:bg-violet-500/10 blur-3xl" />
          <div className="absolute top-1/2 -left-40 h-72 w-72 rounded-full bg-indigo-400/15 dark:bg-indigo-500/10 blur-3xl" />
          <div className="absolute bottom-0 right-1/3 h-64 w-64 rounded-full bg-fuchsia-400/10 dark:bg-fuchsia-500/5 blur-3xl" />
        </div>
        <div className="container relative max-w-5xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl md:text-6xl lg:text-7xl max-w-4xl mx-auto leading-tight">
            Full-stack starter with{" "}
            <span className="bg-gradient-to-r from-violet-600 via-indigo-600 to-fuchsia-600 dark:from-violet-400 dark:via-indigo-400 dark:to-fuchsia-400 bg-clip-text text-transparent">
              Django
            </span>
            ,{" "}
            <span className="bg-gradient-to-r from-violet-600 via-indigo-600 to-fuchsia-600 dark:from-violet-400 dark:via-indigo-400 dark:to-fuchsia-400 bg-clip-text text-transparent">
              Inertia
            </span>{" "}
            &amp;{" "}
            <span className="bg-gradient-to-r from-violet-600 via-indigo-600 to-fuchsia-600 dark:from-violet-400 dark:via-indigo-400 dark:to-fuchsia-400 bg-clip-text text-transparent">
              React
            </span>
          </h1>
          <p className="mt-8 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            One codebase, one server. Build modern UIs with React and shadcn-ui while Django handles
            routing and auth—no separate SPA or API layer.
          </p>
          <div className="mt-12 flex flex-wrap items-center justify-center gap-4">
            <Button
              size="lg"
              asChild
              className="gap-2 h-12 px-8 text-base bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white border-0 shadow-lg shadow-violet-500/30 hover:shadow-violet-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              <Link href={adminHref}>
                {isSignedIn ? "Open admin" : "Get started"}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button
              variant="outline"
              size="lg"
              asChild
              className="gap-2 h-12 px-8 text-base border-2 hover:border-violet-500/50 hover:bg-violet-500/5 hover:text-foreground transition-all"
            >
              <a href="https://github.com/crenspire/django-react-boilerplate" target="_blank" rel="noopener noreferrer">
                <Github className="h-5 w-5" />
                View on GitHub
              </a>
            </Button>
          </div>
        </div>
      </section>

      <section className="relative border-t border-border bg-gradient-to-b from-muted/50 to-muted/30 dark:from-muted/30 dark:to-muted/10 py-20 md:py-28">
        <div className="container max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-foreground tracking-tight mb-3">
            What&apos;s included
          </h2>
          <p className="text-center text-muted-foreground mb-14 max-w-xl mx-auto text-lg">
            Everything you need to ship a Django-backed app with a polished React frontend.
          </p>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-2xl border border-border bg-card p-6 shadow-sm transition-all duration-300 hover:shadow-xl hover:shadow-black/5 dark:hover:shadow-none hover:border-border hover:-translate-y-1"
              >
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br border mb-5 transition-transform duration-300 group-hover:scale-110 ${feature.iconBg}`}
                >
                  <feature.icon className={`h-6 w-6 ${feature.iconColor}`} />
                </div>
                <h3 className="font-semibold text-foreground text-lg">{feature.title}</h3>
                <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-border bg-muted/20 dark:bg-muted/10 py-10 md:py-12">
        <div className="container max-w-5xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-6">
          <p className="text-sm text-muted-foreground">
            Built by{" "}
            <a
              href="https://github.com/akshaypjoshi"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground hover:underline underline-offset-4"
            >
              Akshay Joshi
            </a>{" "}
            at{" "}
            <a
              href="https://crenspire.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-foreground hover:underline underline-offset-4"
            >
              Crenspire Technologies
            </a>{" "}
            · Open source · MIT
          </p>
          <nav className="flex items-center gap-8">
            <Link
              href={route("home")}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors hover:underline underline-offset-4"
            >
              Home
            </Link>
            <Link
              href={adminHref}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors hover:underline underline-offset-4"
            >
              Admin
            </Link>
            <a
              href="https://github.com/crenspire/django-react-boilerplate"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1.5 hover:underline underline-offset-4"
            >
              <Github className="h-4 w-4" />
              GitHub
            </a>
            <a
              href="https://docs.djangoproject.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-flex items-center gap-1.5 hover:underline underline-offset-4"
            >
              <BookOpen className="h-4 w-4" />
              Docs
            </a>
          </nav>
        </div>
      </footer>
    </div>
  )
}
