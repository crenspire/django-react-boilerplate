/**
 * Resolve a Django route name to a URL.
 *
 * `routes` is the shared `routes` prop from main/routes.py, e.g.
 * { admin_user_edit: "/admin/users/{user_id}/edit/" }.
 */
export function buildRoute(routes, name, params = {}, query = {}) {
  const template = routes?.[name]
  if (!template) {
    throw new Error(`Unknown route "${name}". Expose it in main/routes.py.`)
  }

  const path = template.replace(/\{(\w+)\}/g, (_, key) => {
    if (params[key] === undefined || params[key] === null) {
      throw new Error(`Route "${name}" requires parameter "${key}".`)
    }
    return encodeURIComponent(params[key])
  })

  const search = new URLSearchParams()
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") search.set(key, value)
  })
  const queryString = search.toString()
  return queryString ? `${path}?${queryString}` : path
}

/** True when `url` is the route's path or a path below it (ignoring the query string). */
export function isActivePath(url, path, { exact = false } = {}) {
  const current = (url ?? "").split("?")[0]
  return exact ? current === path : current.startsWith(path)
}
