import { useState, useEffect, useCallback } from "react"

const STORAGE_KEY = "admin-theme"

function getStored() {
  try {
    return window.localStorage.getItem(STORAGE_KEY) === "dark" ? "dark" : "light"
  } catch {
    return "light"
  }
}

export function useTheme() {
  const [theme, setThemeState] = useState(getStored)

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark")
    try {
      window.localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      // Storage can be unavailable (private mode, blocked site data); the theme still applies.
    }
  }, [theme])

  const toggle = useCallback(() => {
    setThemeState((prev) => (prev === "dark" ? "light" : "dark"))
  }, [])

  return { theme, toggle }
}
