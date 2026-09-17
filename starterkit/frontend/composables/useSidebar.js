import { useState, useEffect, useCallback } from "react"

const STORAGE_KEY = "admin-sidebar-open"
const TOGGLE_SHORTCUT = "b"

function getStored() {
  try {
    return window.localStorage.getItem(STORAGE_KEY) !== "false"
  } catch {
    return true
  }
}

/**
 * Sidebar UI state for the shadcn Sidebar: `open` is the desktop expanded /
 * collapsed state (remembered per browser), `openMobile` controls the mobile sheet.
 * ⌘B / Ctrl+B toggles whichever applies.
 */
export function useSidebar(isMobile) {
  const [open, setOpenState] = useState(getStored)
  const [openMobile, setOpenMobile] = useState(false)

  const setOpen = useCallback((value) => {
    setOpenState(value)
    try {
      window.localStorage.setItem(STORAGE_KEY, String(value))
    } catch {
      // Storage unavailable; the sidebar still works for this visit.
    }
  }, [])

  const toggle = useCallback(() => {
    if (isMobile) setOpenMobile((prev) => !prev)
    else setOpen(!open)
  }, [isMobile, open, setOpen])

  useEffect(() => {
    const handleKeydown = (event) => {
      if (event.key === TOGGLE_SHORTCUT && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        toggle()
      }
    }
    window.addEventListener("keydown", handleKeydown)
    return () => window.removeEventListener("keydown", handleKeydown)
  }, [toggle])

  return { open, setOpen, openMobile, setOpenMobile }
}
