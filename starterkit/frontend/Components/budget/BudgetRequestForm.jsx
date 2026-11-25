import { Link } from "@inertiajs/react"
import { Loader2 } from "lucide-react"
import { Button } from "@/Components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/Components/ui/card"
import { Input } from "@/Components/ui/input"
import { Textarea } from "@/Components/ui/textarea"
import { FormField } from "@/Components/admin/FormField"
import { cn } from "@/lib/utils"

const invalid = (errors, field) => (errors[field]?.length ? "border-destructive focus-visible:ring-destructive" : undefined)

export function BudgetRequestForm({ data, setData, errors = {}, processing, disabled = false, onSubmit, cancelHref, submitLabel }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit()
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Request details</CardTitle>
          <CardDescription>A manager reviews every request. You can change it until they do.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-6">
          <FormField label="Title" htmlFor="title" error={errors.title?.[0]} required>
            <Input
              id="title"
              value={data.title}
              onChange={(e) => setData("title", e.target.value)}
              placeholder="e.g. New laptops for the design team"
              maxLength={200}
              disabled={disabled}
              aria-invalid={errors.title?.length ? true : undefined}
              className={cn(invalid(errors, "title"))}
            />
          </FormField>

          <FormField label="Amount (USD)" htmlFor="amount" error={errors.amount?.[0]} required>
            <Input
              id="amount"
              value={data.amount}
              onChange={(e) => setData("amount", e.target.value)}
              inputMode="decimal"
              placeholder="0.00"
              disabled={disabled}
              aria-invalid={errors.amount?.length ? true : undefined}
              className={cn("max-w-xs", invalid(errors, "amount"))}
            />
          </FormField>

          <FormField
            label="Business justification"
            htmlFor="justification"
            error={errors.justification?.[0]}
            description="Explain what the money is for and why it is needed."
            required
          >
            <Textarea
              id="justification"
              value={data.justification}
              onChange={(e) => setData("justification", e.target.value)}
              rows={6}
              maxLength={5000}
              disabled={disabled}
              aria-invalid={errors.justification?.length ? true : undefined}
              className={cn(invalid(errors, "justification"))}
            />
          </FormField>
        </CardContent>
        <CardFooter className="gap-2 border-t pt-6">
          {!disabled && (
            <Button type="submit" disabled={processing}>
              {processing && <Loader2 className="animate-spin" />}
              {submitLabel}
            </Button>
          )}
          <Button variant="outline" asChild>
            <Link href={cancelHref}>{disabled ? "Back" : "Cancel"}</Link>
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
