const UNITS = [
  ["year", 60 * 60 * 24 * 365],
  ["month", 60 * 60 * 24 * 30],
  ["week", 60 * 60 * 24 * 7],
  ["day", 60 * 60 * 24],
  ["hour", 60 * 60],
  ["minute", 60],
]

/** "3 days ago", "just now", … for an ISO timestamp. */
export function formatRelativeTime(isoString, now = new Date(), locale = undefined) {
  const seconds = Math.round((new Date(isoString).getTime() - now.getTime()) / 1000)
  const formatter = new Intl.RelativeTimeFormat(locale, { numeric: "auto" })
  for (const [unit, unitSeconds] of UNITS) {
    if (Math.abs(seconds) >= unitSeconds) {
      return formatter.format(Math.round(seconds / unitSeconds), unit)
    }
  }
  return "just now"
}
