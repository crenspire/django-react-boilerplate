from dataclasses import dataclass


@dataclass(frozen=True)
class ListQueryDTO:
    """
    Raw list-page query as parsed from the request.

    Values are not validated here; services decide which ordering is allowed
    and clamp page numbers.
    """

    search: str
    order_by: str
    page: int
    page_size: int


@dataclass(frozen=True)
class DeleteResultDTO:
    success: bool
    message: str
