import { useState, useEffect, useCallback } from "react"

const STORAGE_KEY = "admin-sidebar-open"
const MOBILE_MEDIA = "(max-width: 767px)"

function getStored() {
  if (typeof window === "undefined") return true
  if (window.matchMedia(MOBILE_MEDIA).matches) return false
  const v = window.localStorage.getItem(STORAGE_KEY)
  if (v === "false") return false
  if (v === "true") return true
  return true
}

export function useSidebar() {
  const [sidebarOpen, setSidebarOpen] = useState(getStored)

  useEffect(() => {
    setSidebarOpen(getStored())
  }, [])

  useEffect(() => {
    if (typeof window === "undefined") return
    if (window.matchMedia(MOBILE_MEDIA).matches) return
    window.localStorage.setItem(STORAGE_KEY, String(sidebarOpen))
  }, [sidebarOpen])

  useEffect(() => {
    if (typeof window === "undefined") return
    const mql = window.matchMedia(MOBILE_MEDIA)
    const handler = () => {
      if (mql.matches) setSidebarOpen(false)
    }
    mql.addEventListener("change", handler)
    return () => mql.removeEventListener("change", handler)
  }, [])

  const toggle = useCallback(() => {
    setSidebarOpen((prev) => !prev)
  }, [])

  const close = useCallback(() => {
    setSidebarOpen(false)
  }, [])

  return { sidebarOpen, toggle, close }
}
