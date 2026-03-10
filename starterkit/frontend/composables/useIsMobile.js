import { useState, useEffect } from "react"

const MEDIA_QUERY = "(max-width: 767px)"

export function useIsMobile() {
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    if (typeof window === "undefined") return
    const mql = window.matchMedia(MEDIA_QUERY)
    const handler = () => setIsMobile(mql.matches)
    handler()
    mql.addEventListener("change", handler)
    return () => mql.removeEventListener("change", handler)
  }, [])

  return isMobile
}
