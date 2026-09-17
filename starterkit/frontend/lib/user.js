export function getDisplayName(user) {
  if (!user) return "User"
  const full = [user.first_name, user.last_name].filter(Boolean).join(" ")
  return full || user.username || user.email || "User"
}

export function getUserInitials(user) {
  if (!user) return "U"
  const first = user.first_name ?? ""
  const last = user.last_name ?? ""
  if (first && last) return `${first[0]}${last[0]}`.toUpperCase()
  const name = first || user.username || user.email || ""
  return name ? name.slice(0, 2).toUpperCase() : "U"
}
