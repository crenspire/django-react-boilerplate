import { describe, expect, it } from "vitest"
import { csrfHeaders, readCookie } from "./csrf"

describe("readCookie", () => {
  it("finds a cookie by exact name", () => {
    expect(readCookie("a=1; csrftoken=abc; b=2", "csrftoken")).toBe("abc")
    expect(readCookie("xcsrftoken=nope", "csrftoken")).toBe("")
    expect(readCookie("", "csrftoken")).toBe("")
  })
})

describe("csrfHeaders", () => {
  it("sends Django's token and ignores other frameworks' XSRF-TOKEN cookie", () => {
    const cookies = "PHPSESSID=x; XSRF-TOKEN=eyJpdiI6ImxhcmF2ZWwifQ%3D%3D; csrftoken=djangoToken123"
    expect(csrfHeaders(cookies)).toEqual({ "X-CSRFToken": "djangoToken123" })
  })

  it("returns no header when the cookie is missing", () => {
    expect(csrfHeaders("PHPSESSID=x")).toEqual({})
  })
})
