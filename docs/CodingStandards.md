# Coding Standards

## General Rules

- Preserve current architecture.
- Keep changes focused.
- Avoid unnecessary migrations.
- Do not rename files, classes, fields, or apps without a clear reason.
- Prefer readable explicit code over clever abstractions.
- Update documentation when architecture, workflow, routes, or conventions change.

## Django Standards

- Keep `backend/bim/` configuration-only.
- Put business logic in the owning app.
- Keep app labels `bim_stock` and `bim_accounts`.
- Soft delete uses `isactive`.
- SKU is auto-generated.
- Preserve admin readability for non-technical staff.
- Keep SQL Anywhere compatibility considerations in mind.

## Backend Placement

- Models: `models.py`
- Admin: `admin.py`
- API serializers: `serializers.py`
- API views: `api_views.py`
- API URLs: `api_urls.py`
- Reusable read queries: `selectors.py`
- Permission/app constants: `constants.py`
- Complex writes: add `services.py` when needed

Views should be thin. Serializers may validate API payloads. Services should own multi-step business workflows when those workflows grow.

## React Standards

- Keep editable frontend source under `frontend/src/`.
- Keep `App.jsx` lightweight.
- Add page logic under `routes/` or `pages/`.
- Extract reusable components only when reused or clearly feature-specific.
- Put reusable visual primitives in `frontend/src/components/ui/`.
- Do not import `lucide-react` directly in pages; use `constants/icons.js`.
- Use `statusStyles.js` for status badges.
- Use `uiRegistry.js` for tones and workflow metadata.
- Use `hooks/useTheme.js` for theme behavior.
- Use `utils/formatters.js` for shared display formatting.

## Tailwind Standards

- Follow `DesignSystem.md`.
- Keep the compact enterprise dashboard style.
- Use black/white/zinc/orange brand language.
- Avoid random font sizes and one-off color systems.
- Tables must support horizontal overflow.
- Button/icon spacing should remain consistent.

## API Standards

- Use Django session auth and CSRF.
- Require explicit permissions for stock API actions.
- Use backend-provided `initial_data.api` URLs where possible.
- Add frontend services only when API logic is shared across pages.

## Documentation Standards

- Documentation should describe the current codebase.
- Avoid old implementation history.
- Cross-reference instead of duplicating large sections.
- Keep docs concise enough to stay maintainable.
