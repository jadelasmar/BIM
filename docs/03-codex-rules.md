# Codex Rules

Keep work focused, direct, and aligned with the existing Django architecture.

## Work Style

- Inspect relevant files before editing.
- Apply changes directly when the task is clear.
- Keep replies concise.
- Work one task at a time.
- Avoid unrelated refactors.
- Do not rename files, classes, fields, or apps unnecessarily.
- Ask before destructive operations.
- Preserve user changes in the working tree.

## Architecture Rules

- Django is the backend, auth layer, admin, API provider, and source of truth.
- React/Vite/Tailwind is the operational frontend.
- Node.js is frontend build tooling only.
- Django admin must remain usable for non-technical staff.
- Use Django auth, groups, and permissions.
- Do not add public sign-up.
- Keep internal user emails unique.
- Keep BIM Nexus modular.
- Add separate Django apps/modules only when a workflow has its own data and process.

## BIM Stock Rules

- Preserve SKU generation unless explicitly asked.
- Product is a product definition.
- ProductUnit is a physical stock item.
- Quantity should be calculated from active ProductUnit records.
- Soft delete uses `isactive`.
- Preserve current model field names such as `descript`, `crdate`, and `isactive`.
- Avoid unnecessary migrations.

## Scope Rules

Do not add:
- accounting workflows
- invoice workflows
- payment workflows
- financial posting workflows
- ticketing or Tasklogger replacement workflows

Use `Clients`, not Sites, for this phase.

## UI Rules

- Keep BIM Nexus black/white/orange styling.
- Keep layouts compact and enterprise-focused.
- Use real backend data where available.
- Do not add fake/demo data as real UI data.
- Keep future modules visible as disabled/Coming later when useful.
- Use shared icon/tone registries:
  - `bim/ui_registry.py`
  - `frontend/src/uiRegistry.js`

## Checks

Run relevant checks before finishing:

- `python manage.py check`
- `python manage.py makemigrations --check` when backend/models may be affected
- `python manage.py test` when behavior changes
- `npm run build` from `frontend/` when React changes
- `git diff --check`

## Documentation

Update docs when behavior, workflow, routes, architecture, or roadmap changes.

Primary docs:
- `docs/START-HERE.md`
- `docs/current-focus.md`
- `docs/00-project-overview.md`
- `docs/01-current-structure.md`
- `docs/02-roadmap.md`
- `docs/04-ui-progress.md`
- `docs/05-development-progress.md`
