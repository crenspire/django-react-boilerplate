from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class AssignRoleInputDTO:
    user_id: int
    role: str


@dataclass(frozen=True)
class AssignRoleResultDTO:
    success: bool
    message: str
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None
