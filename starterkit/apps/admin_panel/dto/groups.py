from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class GroupListItemDTO:
    id: int
    name: str
    user_count: int
    permission_count: int
    can_edit: bool
    can_delete: bool


@dataclass(frozen=True)
class GroupFormInputDTO:
    name: str
    permission_ids: tuple[int, ...]


@dataclass(frozen=True)
class GroupFormResultDTO:
    """
    Result of a create or update.

    On failure `page_props` holds the props to re-render the form page with.
    """

    success: bool
    group_id: int | None
    message: str
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None
