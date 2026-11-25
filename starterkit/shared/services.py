from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Page, Paginator
from django.db.models import QuerySet

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def ensure_allowed(allowed: bool) -> None:
    """Raise PermissionDenied (rendered by Django as a 403) when a policy check fails."""
    if not allowed:
        raise PermissionDenied


def paginate(queryset: QuerySet, *, page: int, page_size: int) -> tuple[Page, dict]:
    """
    Return the requested page and its pagination props.

    Page size is clamped to 1..MAX_PAGE_SIZE and out-of-range pages fall back
    to the nearest valid page.
    """

    page_size = min(max(page_size, 1), MAX_PAGE_SIZE)
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    return page_obj, {
        "page": page_obj.number,
        "page_size": page_size,
        "total": paginator.count,
        "total_pages": paginator.num_pages,
    }


def validation_errors(exc: ValidationError) -> dict[str, list[str]]:
    """Convert a Django ValidationError into the {field: [messages]} shape the pages expect."""
    if not hasattr(exc, "error_dict"):
        return {"non_field_errors": list(exc.messages)}
    errors = {}
    for field, messages in exc.message_dict.items():
        key = "non_field_errors" if field == "__all__" else field
        errors.setdefault(key, []).extend(messages)
    return errors


def merge_errors(*error_dicts: dict[str, list[str]]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {}
    for errors in error_dicts:
        for field, messages in errors.items():
            merged.setdefault(field, []).extend(messages)
    return merged
