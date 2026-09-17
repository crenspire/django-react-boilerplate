import { useCallback } from "react"
import { usePage } from "@inertiajs/react"
import { buildRoute } from "@/lib/route"

/** Returns route(name, params?, query?) backed by the routes Django shares with every page. */
export function useRoute() {
  const { routes } = usePage().props
  return useCallback((name, params, query) => buildRoute(routes, name, params, query), [routes])
}
