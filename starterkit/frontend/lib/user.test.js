import { describe, expect, it } from "vitest"
import { getDisplayName, getUserInitials } from "./user"

describe("getDisplayName", () => {
  it("prefers full name, then username, then email", () => {
    expect(getDisplayName({ first_name: "Ada", last_name: "Lovelace", username: "ada" })).toBe("Ada Lovelace")
    expect(getDisplayName({ username: "ada", email: "ada@example.com" })).toBe("ada")
    expect(getDisplayName({ email: "ada@example.com" })).toBe("ada@example.com")
    expect(getDisplayName(null)).toBe("User")
  })
})

describe("getUserInitials", () => {
  it("uses first and last initials when both exist", () => {
    expect(getUserInitials({ first_name: "ada", last_name: "lovelace" })).toBe("AL")
  })

  it("falls back to the first two characters of a name", () => {
    expect(getUserInitials({ first_name: "ada" })).toBe("AD")
    expect(getUserInitials({ username: "root" })).toBe("RO")
    expect(getUserInitials({})).toBe("U")
  })
})
