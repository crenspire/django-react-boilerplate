import { useCallback, useEffect, useRef, useState } from "react"
import { router } from "@inertiajs/react"
import { useRoute } from "@/composables/useRoute"

const SEARCH_DELAY_MS = 300

/**
 * Search / sort / pagination state for a server-filtered list page.
 * Django applies the filters; this only keeps the URL in sync with the inputs.
 */
export function useListFilters(routeName, filters) {
  const route = useRoute()
  const [search, setSearch] = useState(filters.search)
  // Last search we sent, so a response for it doesn't overwrite newer typing.
  const requestedSearch = useRef(filters.search)

  const visit = useCallback(
    (query) => {
      const params = { search: filters.search, order_by: filters.order_by, ...query }
      requestedSearch.current = params.search
      router.get(route(routeName), params, { preserveState: true, preserveScroll: true, replace: true })
    },
    [filters.search, filters.order_by, route, routeName]
  )

  // Follow changes that did not come from this input (e.g. redirect after a delete).
  useEffect(() => {
    if (filters.search !== requestedSearch.current) {
      requestedSearch.current = filters.search
      setSearch(filters.search)
    }
  }, [filters.search])

  useEffect(() => {
    if (search === requestedSearch.current) return undefined
    const timer = setTimeout(() => visit({ search, page: undefined }), SEARCH_DELAY_MS)
    return () => clearTimeout(timer)
  }, [search, visit])

  const sortBy = useCallback((orderBy) => visit({ order_by: orderBy, page: undefined }), [visit])

  const pageUrl = useCallback(
    (page) => route(routeName, {}, { search: filters.search, order_by: filters.order_by, page }),
    [filters.search, filters.order_by, route, routeName]
  )

  return { search, setSearch, sortBy, pageUrl }
}
