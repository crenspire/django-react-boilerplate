import React from "react"
import { createInertiaApp, router } from "@inertiajs/react"
import { createRoot } from "react-dom/client"
import "./main.css"

// Apply saved theme before first paint to avoid flash
const savedTheme = typeof localStorage !== "undefined" ? localStorage.getItem("admin-theme") : null
if (savedTheme === "dark") document.documentElement.classList.add("dark")
else document.documentElement.classList.remove("dark")

// CSRF token for non-GET requests (Django). Updated from meta tag and on each Inertia navigate.
let csrfToken = ""
if (typeof document !== "undefined") {
  const meta = document.querySelector('meta[name="csrf-token"]')
  if (meta) csrfToken = meta.getAttribute("content") || ""
}

const pages = import.meta.glob("./Pages/**/*.jsx")

createInertiaApp({
  resolve: async (name) => {
    const path = `./Pages/${name}.jsx`
    const loader = pages[path]
    if (!loader) {
      throw new Error(`Unknown Inertia page: ${name}`)
    }
    const mod = await loader()
    const Page = mod.default
    const Layout = mod.default?.layout ?? mod.layout
    if (Layout) {
      return (props) =>
        React.createElement(
          Layout,
          props,
          React.createElement(Page, props)
        )
    }
    return Page
  },
  defaults: {
    visitOptions: (href, options) => ({
      ...options,
      headers: {
        ...options.headers,
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
      },
    }),
  },
  setup({ el, App, props }) {
    if (props.initialPage?.props?.csrf_token) {
      csrfToken = props.initialPage.props.csrf_token
    }
    router.on("navigate", (e) => {
      const token = e.detail?.page?.props?.csrf_token
      if (token) csrfToken = token
    })
    createRoot(el).render(React.createElement(App, props))
  },
})
