from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class UserListItemDTO:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_superuser: bool
    is_active: bool
    can_edit: bool
    can_delete: bool


@dataclass(frozen=True)
class UserFormInputDTO:
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    is_superuser: bool
    is_active: bool
    group_ids: tuple[int, ...]
    password: str  # Required on create; "" keeps the current password on update.


@dataclass(frozen=True)
class UserFormResultDTO:
    """
    Result of a create or update.

    On failure `page_props` holds the props to re-render the form page with.
    """

    success: bool
    user_id: int | None
    message: str
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None
