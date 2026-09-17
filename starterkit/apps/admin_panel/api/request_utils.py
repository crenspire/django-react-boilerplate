import json

from django.http import HttpRequest

from apps.admin_panel.dto.common import ListQueryDTO

TRUE_VALUES = (True, 1, "1", "true", "on")


def get_request_data(request: HttpRequest) -> dict:
    """
    Return POST data as a dict. Supports both form-encoded and JSON body (Inertia).
    For form-encoded, list values (e.g. group_ids) are kept as lists; single values unwrapped.
    """
    raw = {}
    if request.content_type and "application/json" in request.content_type and request.body:
        try:
            raw = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            pass
    elif request.POST:
        raw = {k: v if len(v) != 1 else v[0] for k, v in request.POST.lists()}
    if not isinstance(raw, dict):
        return {}
    return raw


def parse_str(value) -> str:
    return value if isinstance(value, str) else ""


def parse_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_bool(value) -> bool:
    return value in TRUE_VALUES


def parse_id_list(value) -> tuple[int, ...]:
    if value is None or value == "":
        return ()
    values = value if isinstance(value, list) else [value]
    return tuple(int(v) for v in values if str(v).isdigit())


def parse_list_query(request: HttpRequest) -> ListQueryDTO:
    # Only type conversion happens here; services validate ordering and page bounds.
    return ListQueryDTO(
        search=request.GET.get("search", "").strip(),
        order_by=request.GET.get("order_by", ""),
        page=parse_int(request.GET.get("page"), 1),
        page_size=parse_int(request.GET.get("page_size"), 25),
    )


def client_ip(request: HttpRequest) -> str:
    # REMOTE_ADDR only: X-Forwarded-For is client-controlled unless a trusted
    # proxy rewrites it. Behind a proxy, set REMOTE_ADDR from the proxy header
    # in your server/middleware configuration.
    return request.META.get("REMOTE_ADDR", "")
