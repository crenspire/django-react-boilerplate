import { Search, X } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Input } from "@/Components/ui/input"

/** Table filter input. The page decides when to apply the value (e.g. debounced). */
export function SearchBar({ value, onChange, placeholder = "Search…" }) {
  return (
    <div className="relative w-full sm:w-72">
      <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        type="search"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
        className="h-9 pl-8 pr-8 [&::-webkit-search-cancel-button]:hidden"
      />
      {value && (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="absolute right-1 top-1/2 h-7 w-7 -translate-y-1/2 text-muted-foreground"
          onClick={() => onChange("")}
          aria-label="Clear search"
        >
          <X />
        </Button>
      )}
    </div>
  )
}
