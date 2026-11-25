import { describe, expect, it } from "vitest"
import { formatAmount } from "./money"

describe("formatAmount", () => {
  it("formats decimal strings as currency", () => {
    expect(formatAmount("1500.5")).toBe("$1,500.50")
    expect(formatAmount("0.01")).toBe("$0.01")
  })

  it("shows a dash for missing or invalid values", () => {
    expect(formatAmount("")).toBe("—")
    expect(formatAmount(null)).toBe("—")
    expect(formatAmount("abc")).toBe("—")
  })
})
