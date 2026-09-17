"""
Named Django routes exposed to the frontend.

Django owns routing; React resolves these names instead of hardcoding paths.
Parameters appear as `{name}` placeholders, e.g. "/admin/users/{user_id}/edit/".
"""

import re

from django.urls import get_resolver, get_script_prefix

EXPOSED_ROUTE_NAMES = (
    "home",
    "login",
    "logout",
    "admin_dashboard",
    "admin_users",
    "admin_user_create",
    "admin_user_edit",
    "admin_user_delete",
    "admin_groups",
    "admin_group_create",
    "admin_group_edit",
    "admin_group_delete",
)

_PLACEHOLDER = re.compile(r"%\((\w+)\)s")


def route_map() -> dict[str, str]:
    resolver = get_resolver()
    prefix = get_script_prefix()
    routes = {}
    for name in EXPOSED_ROUTE_NAMES:
        # reverse_dict maps a name to [(possibilities, pattern, defaults, converters)];
        # each possibility is (format string, parameter names), e.g.
        # ("admin/users/%(user_id)s/edit/", ["user_id"]).
        possibilities = resolver.reverse_dict.getlist(name)
        if not possibilities:
            raise LookupError(f"Route {name!r} is exposed to the frontend but not defined in urls.py")
        format_string, _params = possibilities[0][0][0]
        routes[name] = prefix + _PLACEHOLDER.sub(r"{\1}", format_string)
    return routes
