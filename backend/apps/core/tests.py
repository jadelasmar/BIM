import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase, override_settings

from .templatetags import vite


class ViteManifestTests(SimpleTestCase):
    def test_debug_mode_reloads_changed_manifest(self):
        with TemporaryDirectory() as temporary_directory:
            base_dir = Path(temporary_directory)
            manifest_path = base_dir / "static" / "frontend" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps({"src/main.jsx": {"file": "assets/first.js"}}),
                encoding="utf-8",
            )

            if hasattr(vite._vite_manifest, "cache_clear"):
                vite._vite_manifest.cache_clear()

            with override_settings(BASE_DIR=base_dir, DEBUG=True):
                first_tags = str(vite.vite_react_assets())
                manifest_path.write_text(
                    json.dumps({"src/main.jsx": {"file": "assets/second.js"}}),
                    encoding="utf-8",
                )
                second_tags = str(vite.vite_react_assets())

        self.assertIn("assets/first.js", first_tags)
        self.assertIn("assets/second.js", second_tags)
        self.assertNotIn("assets/first.js", second_tags)
