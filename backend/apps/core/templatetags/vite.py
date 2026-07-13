import json
from functools import lru_cache

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


register = template.Library()


def _read_vite_manifest():
    manifest_path = settings.BASE_DIR / "static" / "frontend" / "manifest.json"
    with manifest_path.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


@lru_cache(maxsize=1)
def _cached_vite_manifest():
    return _read_vite_manifest()


def _vite_manifest():
    if settings.DEBUG:
        return _read_vite_manifest()
    return _cached_vite_manifest()


@register.simple_tag
def vite_react_assets(entry="src/main.jsx"):
    manifest = _vite_manifest()
    chunk = manifest[entry]
    css_tags = format_html_join(
        "\n",
        '<link rel="stylesheet" href="{}">',
        ((static(f"frontend/{css_file}"),) for css_file in chunk.get("css", [])),
    )
    script_tag = format_html(
        '<script type="module" src="{}"></script>',
        static(f"frontend/{chunk['file']}"),
    )

    return mark_safe(f"{css_tags}\n{script_tag}")
