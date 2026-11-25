from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class BudgetRequestInputDTO:
    title: str
    amount: str
    justification: str


@dataclass(frozen=True)
class ReviewInputDTO:
    decision: str
    note: str


@dataclass(frozen=True)
class BudgetRequestResultDTO:
    success: bool
    request_id: int | None
    message: str
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None = None
