from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class LoginInputDTO:
    """
    Immutable container for login request data.
    """

    username: str
    password: str
    next_url: str
    default_redirect_url: str
    client_ip: str


@dataclass(frozen=True)
class LoginResultDTO:
    """
    Result of attempting to log a user in.

    On failure `page_props` holds the props to re-render the login page with.
    """

    success: bool
    redirect_url: str | None
    errors: Mapping[str, Sequence[str]]
    page_props: Mapping[str, Any] | None
