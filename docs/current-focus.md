# Current Focus

## Current Work

- Keep documentation aligned with the current Django implementation.
- BIM Stock is the active implemented module.
- Django is the backend/source of truth; React with Tailwind CSS is the Command Center frontend.
- Node.js is frontend build tooling only.
- Login UI has been updated from the provided Figma CSS/spec and centralized BIM Nexus brand assets under `static/bim/assets/brand/`.
- React/Vite/Tailwind source now exists under `frontend/src/`.
- Built React assets are served from `static/frontend/`.

## Do Not Modify Unnecessarily

- SKU generation logic on `Product`.
- Existing model field names such as `descript`, `printed`, `crdate`, and `isactive`.
- Current `ProductUnit` statuses unless a focused status migration is planned.
- Django auth behavior.
- Django admin availability and staff usability.
- BIM Stock templates while working on unrelated modules.

## Immediate Next Implementation Goals

1. Harden BIM Stock permissions and status behavior.
2. Add stock movement audit history.
3. Add Companies / Sites before workflows that need company/site references.
4. Expand React screens only when the matching Django workflow/API exists.
