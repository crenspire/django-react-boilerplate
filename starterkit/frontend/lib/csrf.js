// Django defaults (CSRF_COOKIE_NAME / CSRF_HEADER_NAME). Keep in sync with main/settings.py.
export const CSRF_COOKIE_NAME = "csrftoken"
export const CSRF_HEADER_NAME = "X-CSRFToken"

export function readCookie(cookieString, name) {
  const prefix = `${name}=`
  const match = (cookieString ?? "").split("; ").find((cookie) => cookie.startsWith(prefix))
  return match ? decodeURIComponent(match.slice(prefix.length)) : ""
}

/** Headers carrying Django's CSRF token, or {} when the cookie is not set yet. */
export function csrfHeaders(cookieString) {
  const token = readCookie(cookieString, CSRF_COOKIE_NAME)
  return token ? { [CSRF_HEADER_NAME]: token } : {}
}
