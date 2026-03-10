import * as React from "react"
import { Input } from "@/Components/ui/input"
import { Button } from "@/Components/ui/button"
import { Search, X } from "lucide-react"

export function SearchBar({ value, onChange, onSearch, onClear, placeholder = "Search..." }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch?.()
  }

  const handleClear = () => {
    onChange?.("")
    onClear?.()
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-center gap-2">
      <div className="relative flex-1 max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          value={value ?? ""}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={placeholder}
          className="pl-9 pr-9"
        />
        {value && (
          <button
            type="button"
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
      <Button type="submit" variant="secondary" size="sm">
        Search
      </Button>
    </form>
  )
}
