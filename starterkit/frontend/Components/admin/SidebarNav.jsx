import { Link } from "@inertiajs/react"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/Components/ui/sidebar"

/**
 * Main navigation, one SidebarGroup per section. `items` are
 * { section, label, href, icon, active } built by the layout.
 */
export function SidebarNav({ items, onNavigate }) {
  const sections = []
  for (const item of items) {
    let section = sections.find((s) => s.name === item.section)
    if (!section) {
      section = { name: item.section, items: [] }
      sections.push(section)
    }
    section.items.push(item)
  }

  return sections.map((section) => (
    <SidebarGroup key={section.name}>
      <SidebarGroupLabel>{section.name}</SidebarGroupLabel>
      <SidebarMenu>
        {section.items.map((item) => (
          <SidebarMenuItem key={item.href}>
            <SidebarMenuButton asChild isActive={item.active} tooltip={item.label}>
              <Link href={item.href} onClick={onNavigate} aria-current={item.active ? "page" : undefined}>
                <item.icon />
                <span>{item.label}</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  ))
}
