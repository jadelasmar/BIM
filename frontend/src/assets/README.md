# BIM Nexus Frontend Assets

This folder is the staging source for the future React/Tailwind frontend.
Django remains the backend/source of truth. Node.js should be used only for
frontend build tooling when the React setup is introduced.

Current source buckets:

```text
frontend/src/assets/
|-- brand/
```

Guidelines:

- Keep BIM Nexus logos and brand marks in `brand/`.
- Prefer SVG for logos and icons when available.
- Use lowercase kebab-case names, for example `logo-primary.svg`.
- Use `brand/logo-primary.svg` and `brand/logo-white.svg` as the primary React logo assets.
- Use `brand/co-brand-built-for-bimpos.svg` when the UI, reports, or exports need the BIMPOS footer/co-brand mark.

The React/Vite app imports frontend assets from this folder.
