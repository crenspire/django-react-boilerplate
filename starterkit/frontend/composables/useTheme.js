import { useState, useEffect, useCallback } from "react"

const STORAGE_KEY = "admin-theme"

function getStored() {
  if (typeof window === "undefined") return "light"
  return window.localStorage.getItem(STORAGE_KEY) || "light"
}

function setClass(theme) {
  if (typeof document === "undefined") return
  const root = document.documentElement
  if (theme === "dark") {
    root.classList.add("dark")
  } else {
    root.classList.remove("dark")
  }
}

export function useTheme() {
  const [theme, setThemeState] = useState(getStored)

  useEffect(() => {
    setClass(theme)
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, theme)
    }
  }, [theme])

  const toggle = useCallback(() => {
    setThemeState((prev) => (prev === "dark" ? "light" : "dark"))
  }, [])

  const setTheme = useCallback((value) => {
    if (value === "dark" || value === "light") setThemeState(value)
  }, [])

  return { theme, toggle, setTheme }
}
