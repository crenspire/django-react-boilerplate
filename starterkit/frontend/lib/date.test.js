import { describe, expect, it } from "vitest"
import { formatRelativeTime } from "./date"

const now = new Date("2026-09-17T12:00:00Z")

describe("formatRelativeTime", () => {
  it("returns 'just now' for under a minute", () => {
    expect(formatRelativeTime("2026-09-17T11:59:30Z", now, "en")).toBe("just now")
  })

  it("picks the largest whole unit", () => {
    expect(formatRelativeTime("2026-09-17T11:55:00Z", now, "en")).toBe("5 minutes ago")
    expect(formatRelativeTime("2026-09-16T12:00:00Z", now, "en")).toBe("yesterday")
    expect(formatRelativeTime("2026-09-03T12:00:00Z", now, "en")).toBe("2 weeks ago")
    expect(formatRelativeTime("2025-09-17T12:00:00Z", now, "en")).toBe("last year")
  })
})
