// Amounts arrive from Django as exact decimal strings ("1500.00"); they are only formatted here.
const CURRENCY = "USD"

/** "1500.5" → "$1,500.50". Returns "—" for empty or non-numeric input. */
export function formatAmount(amount, locale = "en-US") {
  if (amount === null || amount === undefined || amount === "") return "—"
  const value = Number(amount)
  if (!Number.isFinite(value)) return "—"
  return new Intl.NumberFormat(locale, { style: "currency", currency: CURRENCY }).format(value)
}
