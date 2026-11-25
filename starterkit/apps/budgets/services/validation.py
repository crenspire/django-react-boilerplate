from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from apps.budgets.domain.models import MAX_AMOUNT, REVIEW_OUTCOMES, BudgetRequest, Status
from apps.budgets.dto.budget_requests import BudgetRequestInputDTO, ReviewInputDTO

TITLE_MAX_LENGTH = BudgetRequest._meta.get_field("title").max_length
JUSTIFICATION_MAX_LENGTH = 5000
NOTE_MAX_LENGTH = 2000

REQUIRED = "This field is required."
NOTE_REQUIRED_ON_REJECT = "Explain why the request is rejected."


@dataclass(frozen=True)
class CleanRequest:
    title: str
    amount: Decimal
    justification: str


@dataclass(frozen=True)
class CleanReview:
    status: Status
    note: str


Errors = dict[str, list[str]]


def clean_request_input(data: BudgetRequestInputDTO) -> tuple[CleanRequest | None, Errors]:
    errors: Errors = {}
    title = data.title.strip()
    justification = data.justification.strip()

    _check_text(errors, "title", title, max_length=TITLE_MAX_LENGTH)
    _check_text(errors, "justification", justification, max_length=JUSTIFICATION_MAX_LENGTH)
    amount, amount_error = _parse_amount(data.amount)
    if amount_error:
        errors["amount"] = [amount_error]

    if errors:
        return None, errors
    return CleanRequest(title=title, amount=amount, justification=justification), {}


def clean_review_input(data: ReviewInputDTO) -> tuple[CleanReview | None, Errors]:
    errors: Errors = {}
    note = data.note.strip()

    if data.decision not in REVIEW_OUTCOMES:
        errors["decision"] = ["Choose approve or reject."]
    elif data.decision == Status.REJECTED and not note:
        errors["note"] = [NOTE_REQUIRED_ON_REJECT]
    if len(note) > NOTE_MAX_LENGTH:
        errors["note"] = [f"Keep the note under {NOTE_MAX_LENGTH} characters."]

    if errors:
        return None, errors
    return CleanReview(status=Status(data.decision), note=note), {}


def _check_text(errors: Errors, field: str, value: str, *, max_length: int) -> None:
    if not value:
        errors[field] = [REQUIRED]
    elif len(value) > max_length:
        errors[field] = [f"Keep this under {max_length} characters."]


def _parse_amount(raw: str) -> tuple[Decimal | None, str]:
    raw = raw.strip().replace(",", "")
    if not raw:
        return None, REQUIRED
    try:
        amount = Decimal(raw)
    except InvalidOperation:
        return None, "Enter a valid amount."
    if not amount.is_finite():
        return None, "Enter a valid amount."
    if amount <= 0:
        return None, "The amount must be greater than zero."
    if amount > MAX_AMOUNT:
        return None, f"The amount cannot exceed {MAX_AMOUNT:,}."
    if amount.as_tuple().exponent < -2:
        return None, "Use at most two decimal places."
    return amount.quantize(Decimal("0.01")), ""
