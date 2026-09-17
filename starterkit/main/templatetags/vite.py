"""
{% vite_assets %} renders the script and style tags for the frontend entry.

- Dev mode (VITE_DEV_MODE=True): load modules from the Vite dev server with HMR.
- Otherwise: read the manifest written by `npm run build` and link the hashed
  files through Django's static files.
"""

import json
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

register = template.Library()

DEFAULT_ENTRY = "app.jsx"

# Mirrors @vitejs/plugin-react's preamble; required when Django (not Vite) serves the HTML.
REACT_REFRESH_PREAMBLE = """<script type="module">
import {{ injectIntoGlobalHook }} from "{url}/@react-refresh";
injectIntoGlobalHook(window);
window.$RefreshReg$ = () => {{}};
window.$RefreshSig$ = () => (type) => type;
</script>"""


@register.simple_tag
def vite_assets(entry: str = DEFAULT_ENTRY) -> str:
    if settings.VITE_DEV_MODE:
        return _dev_tags(entry)
    return _build_tags(entry)


def _dev_tags(entry: str) -> str:
    url = settings.VITE_DEV_SERVER_URL.rstrip("/")
    return mark_safe(
        "\n".join(
            [
                format_html(REACT_REFRESH_PREAMBLE, url=url),
                format_html('<script type="module" src="{}/@vite/client"></script>', url),
                format_html('<script type="module" src="{}/{}"></script>', url, entry),
            ]
        )
    )


def _build_tags(entry: str) -> str:
    manifest = load_manifest(str(settings.VITE_MANIFEST_PATH))
    if entry not in manifest:
        raise ImproperlyConfigured(f"Vite entry {entry!r} is missing from {settings.VITE_MANIFEST_PATH}.")

    chunk = manifest[entry]
    css_files, preload_files = _collect_dependencies(manifest, entry)
    parts = [
        format_html_join("\n", '<link rel="stylesheet" href="{}">', ((static(f),) for f in css_files)),
        format_html_join("\n", '<link rel="modulepreload" href="{}">', ((static(f),) for f in preload_files)),
        format_html('<script type="module" src="{}"></script>', static(chunk["file"])),
    ]
    return mark_safe("\n".join(part for part in parts if part))


def _collect_dependencies(manifest: dict, entry: str) -> tuple[list[str], list[str]]:
    """CSS for the entry and its static imports, plus JS chunks to preload."""
    css_files: list[str] = []
    preload_files: list[str] = []
    seen: set[str] = set()

    def visit(key: str, is_entry: bool) -> None:
        if key in seen:
            return
        seen.add(key)
        chunk = manifest[key]
        for css in chunk.get("css", []):
            if css not in css_files:
                css_files.append(css)
        if not is_entry:
            preload_files.append(chunk["file"])
        for imported in chunk.get("imports", []):
            visit(imported, is_entry=False)

    visit(entry, is_entry=True)
    return css_files, preload_files


def load_manifest(path: str) -> dict:
    # Re-read while DEBUG is on so a fresh `npm run build` is picked up without a restart.
    if settings.DEBUG:
        return _read_manifest(path)
    return _read_manifest_cached(path)


def _read_manifest(path: str) -> dict:
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise ImproperlyConfigured(
            f"Vite manifest not found at {manifest_path}. Run `npm run build` in "
            "starterkit/frontend, or set VITE_DEV_MODE=true to use the dev server."
        )
    return json.loads(manifest_path.read_text())


_read_manifest_cached = lru_cache(maxsize=4)(_read_manifest)
