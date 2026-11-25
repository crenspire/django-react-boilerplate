const CURRENCY = "USD"

export function formatAmount(amount, locale = "en-US") {
  if (amount === null || amount === undefined || amount === "") return "—"
  const value = Number(amount)
  if (!Number.isFinite(value)) return "—"
  return new Intl.NumberFormat(locale, { style: "currency", currency: CURRENCY }).format(value)
}
