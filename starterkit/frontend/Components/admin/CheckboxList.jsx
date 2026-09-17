import { Checkbox } from "@/Components/ui/checkbox"
import { cn } from "@/lib/utils"

/** Scrollable, bordered list of checkboxes bound to an array of selected ids. */
export function CheckboxList({
  options,
  selectedIds,
  onChange,
  emptyText,
  disabled = false,
  labelClassName,
  className,
}) {
  const toggle = (id) => {
    onChange(selectedIds.includes(id) ? selectedIds.filter((x) => x !== id) : [...selectedIds, id])
  }

  if (!options.length) {
    return (
      <div className="rounded-lg border border-dashed px-4 py-6 text-center text-sm text-muted-foreground">
        {emptyText}
      </div>
    )
  }

  return (
    <div className={cn("max-h-64 divide-y overflow-y-auto rounded-lg border", className)}>
      {options.map((option) => (
        <label
          key={option.id}
          className={cn(
            "flex items-center gap-3 px-3 py-2 text-sm transition-colors has-[[data-state=checked]]:bg-muted/50",
            disabled ? "cursor-not-allowed opacity-70" : "cursor-pointer hover:bg-muted/50"
          )}
        >
          <Checkbox
            checked={selectedIds.includes(option.id)}
            onCheckedChange={() => toggle(option.id)}
            disabled={disabled}
          />
          <span className={labelClassName}>{option.label}</span>
        </label>
      ))}
    </div>
  )
}
