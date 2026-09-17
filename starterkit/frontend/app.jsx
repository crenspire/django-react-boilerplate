import { createInertiaApp } from "@inertiajs/react"
import { createRoot } from "react-dom/client"
import { csrfHeaders } from "@/lib/csrf"
import "./main.css"

// The saved theme is applied by an inline script in templates/base.html.

const pages = import.meta.glob("./Pages/**/*.jsx")

createInertiaApp({
  title: (title) => (title ? `${title} · Django Inertia Starter` : "Django Inertia Starter"),
  resolve: async (name) => {
    const loader = pages[`./Pages/${name}.jsx`]
    if (!loader) {
      throw new Error(`Unknown Inertia page: ${name}`)
    }
    // Pages declare `Page.layout = (page) => <Layout>{page}</Layout>`; Inertia keeps
    // the layout mounted across visits because its component type never changes.
    return (await loader()).default
  },
  defaults: {
    // Send Django's CSRF token with every visit. The cookie is read per request
    // because Django rotates the token on login.
    visitOptions: (href, options) => ({
      headers: { ...options.headers, ...csrfHeaders(document.cookie) },
    }),
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})
