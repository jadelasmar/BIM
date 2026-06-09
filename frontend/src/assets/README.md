# BIM Nexus Frontend Assets

This folder is the staging source for the future React/Tailwind frontend.
Django remains the backend/source of truth. Node.js should be used only for
frontend build tooling when the React setup is introduced.

Use these buckets:

```text
frontend/src/assets/
|-- brand/
|-- images/
|-- icons/
|-- illustrations/
|-- screenshots/
`-- backgrounds/
```

Guidelines:

- Keep BIM Nexus logos and brand marks in `brand/`.
- Keep screen or product imagery in `images/`.
- Keep standalone UI icons in `icons/`.
- Keep decorative or explanatory graphics in `illustrations/`.
- Keep Figma and screen references in `screenshots/`.
- Keep login, dashboard, and page background assets in `backgrounds/`.
- Prefer SVG for logos and icons when available.
- Use lowercase kebab-case names, for example `logo-primary.svg`.
- Use `brand/logo-primary.svg`, `brand/logo-white.svg`, and `brand/brand-mark.svg` as preferred production assets in React.
- Treat `screenshots/login-dark.png` and `screenshots/login-light.png` as design references only. Do not use them as image slices in the UI.

Current Django templates still load runtime assets from `static/bim/assets/`.
When the React/Vite setup is introduced, import frontend assets from this folder.
