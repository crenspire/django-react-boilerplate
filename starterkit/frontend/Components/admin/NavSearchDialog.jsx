import { LogOut, Moon, Sun } from "lucide-react"
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/Components/ui/command"

/** ⌘K command palette: jump to a page or run a UI action. */
export function NavSearchDialog({ open, onOpenChange, items, theme, onNavigate, onToggleTheme, onLogout }) {
  const run = (action) => {
    onOpenChange(false)
    action()
  }

  return (
    <CommandDialog open={open} onOpenChange={onOpenChange} title="Search" description="Jump to a page or run an action.">
      <CommandInput placeholder="Type a command or search…" />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="Pages">
          {items.map((item) => (
            <CommandItem key={item.href} value={`${item.label} ${item.section}`} onSelect={() => run(() => onNavigate(item.href))}>
              <item.icon />
              <span>{item.label}</span>
              <CommandShortcut className="tracking-normal">{item.section}</CommandShortcut>
            </CommandItem>
          ))}
        </CommandGroup>
        <CommandSeparator />
        <CommandGroup heading="Preferences">
          <CommandItem value="toggle theme dark light mode" onSelect={() => run(onToggleTheme)}>
            {theme === "dark" ? <Sun /> : <Moon />}
            <span>{theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}</span>
          </CommandItem>
          <CommandItem value="log out sign out" onSelect={() => run(onLogout)}>
            <LogOut />
            <span>Log out</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}
