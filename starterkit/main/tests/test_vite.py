import json
import tempfile
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from main.templatetags.vite import vite_assets

MANIFEST = {
    "app.jsx": {
        "file": "assets/app-abc123.js",
        "isEntry": True,
        "css": ["assets/app-def456.css"],
        "imports": ["_vendor.js"],
        "dynamicImports": ["Pages/Home.jsx"],
    },
    "_vendor.js": {"file": "assets/vendor-111.js", "css": ["assets/vendor-222.css"]},
    "Pages/Home.jsx": {"file": "assets/Home-333.js", "isDynamicEntry": True},
}


class ViteAssetsTagTests(SimpleTestCase):
    @override_settings(VITE_DEV_MODE=True, VITE_DEV_SERVER_URL="http://localhost:5173/")
    def test_dev_mode_loads_from_dev_server(self):
        html = vite_assets()
        self.assertIn('from "http://localhost:5173/@react-refresh"', html)
        self.assertIn('<script type="module" src="http://localhost:5173/@vite/client"></script>', html)
        self.assertIn('<script type="module" src="http://localhost:5173/app.jsx"></script>', html)

    def test_build_mode_uses_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            manifest_path.write_text(json.dumps(MANIFEST))
            with override_settings(VITE_DEV_MODE=False, VITE_MANIFEST_PATH=manifest_path, DEBUG=True):
                html = vite_assets()

        self.assertIn('<link rel="stylesheet" href="/static/assets/app-def456.css">', html)
        self.assertIn('<link rel="stylesheet" href="/static/assets/vendor-222.css">', html)
        self.assertIn('<link rel="modulepreload" href="/static/assets/vendor-111.js">', html)
        self.assertIn('<script type="module" src="/static/assets/app-abc123.js"></script>', html)
        # Lazy-loaded pages are fetched on demand, not preloaded.
        self.assertNotIn("Home-333", html)
        self.assertNotIn("5173", html)

    def test_missing_manifest_explains_how_to_fix(self):
        with override_settings(VITE_DEV_MODE=False, VITE_MANIFEST_PATH="/nonexistent/manifest.json", DEBUG=True):
            with self.assertRaisesMessage(ImproperlyConfigured, "npm run build"):
                vite_assets()
