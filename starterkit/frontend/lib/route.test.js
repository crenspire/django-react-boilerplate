import { describe, expect, it } from "vitest"
import { buildRoute, isActivePath } from "./route"

const routes = {
  admin_users: "/admin/users/",
  admin_user_edit: "/admin/users/{user_id}/edit/",
}

describe("buildRoute", () => {
  it("returns static paths", () => {
    expect(buildRoute(routes, "admin_users")).toBe("/admin/users/")
  })

  it("fills and encodes parameters", () => {
    expect(buildRoute(routes, "admin_user_edit", { user_id: 7 })).toBe("/admin/users/7/edit/")
    expect(buildRoute(routes, "admin_user_edit", { user_id: "a/b" })).toBe("/admin/users/a%2Fb/edit/")
  })

  it("appends non-empty query parameters", () => {
    expect(buildRoute(routes, "admin_users", {}, { search: "bob", page: 2, order_by: "" })).toBe(
      "/admin/users/?search=bob&page=2"
    )
  })

  it("throws for unknown routes and missing parameters", () => {
    expect(() => buildRoute(routes, "nope")).toThrow(/Unknown route/)
    expect(() => buildRoute(routes, "admin_user_edit")).toThrow(/requires parameter "user_id"/)
  })
})

describe("isActivePath", () => {
  it("matches nested paths unless exact", () => {
    expect(isActivePath("/admin/users/3/edit/?x=1", "/admin/users/")).toBe(true)
    expect(isActivePath("/admin/users/", "/admin/", { exact: true })).toBe(false)
    expect(isActivePath("/admin/?page=2", "/admin/", { exact: true })).toBe(true)
  })
})
