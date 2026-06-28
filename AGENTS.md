# Repository Guidelines

## Project Identity

BIM Nexus is an internal IT operations platform for BIM POS, not an accounting ERP. It manages stock, products, assets, records, movement history, suppliers, clients, documents, and tracking. Stack: Django/DRF, SQLite, React, Vite, and Tailwind CSS.

## Mandatory Startup Before Changes

Before editing, read `docs/README.md`, then relevant docs such as `Backend.md`, `Frontend.md`, `Database.md`, `Development.md`, `Roadmap.md`, `CodingStandards.md`, `CodeMap.md`, or `DesignSystem.md`. Inspect implementation first.

## Project Structure & Module Organization

- `backend/`: Django apps, templates, generated static, media.
- `backend/bim/`: configuration only.
- `backend/apps/core/`: React shell, Command Center data, UI config.
- `backend/apps/accounts/`: login, setup links, admin.
- `backend/apps/stock/`: stock models, admin, APIs, serializers, selectors, roles, tests, migrations.
- `frontend/src/`: editable React source.
- `frontend/src/routes/AppRouter.jsx`: main operational UI and route selection.
- `frontend/src/components/ui/`: reusable UI primitives.
- `docs/`: project source of truth.

Do not edit generated files under `backend/static/frontend/`.

## Build, Test, And Development

Backend commands from `backend/`:

```powershell
python manage.py migrate
python manage.py runserver
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Frontend commands from `frontend/`:

```powershell
npm install
npm run dev
npm run build
```

Run `git diff --check` before finishing.

## Coding Style

Preserve architecture. Avoid unrelated refactors, unnecessary migrations, duplicate code, and renames unless required. Prefer readable code.

Django: soft delete uses `isactive`; SKU is auto-generated; app labels stay `bim_stock` and `bim_accounts`; admin must stay readable; keep SQL Anywhere compatibility in mind.

React: keep `App.jsx` lightweight, reuse UI primitives, support dark/light modes, use `constants/icons.js`, `statusStyles.js`, and `utils/formatters.js`.

## Inventory Domain Rules

Products define item information. Product units represent physical stock. Stock changes through receiving, delivery, temporary issue, damage, return, reservation, or internal movement. Records are operational, not financial invoices. Use `RCV-YYYY-####` and `DLV-YYYY-####`; movement history must remain auditable.

## Documentation Requirements

Update docs after meaningful changes. Models affect `Database.md` and `Backend.md`; APIs affect `Backend.md`; UI affects `Frontend.md`, `DesignSystem.md`, and `CodeMap.md`; setup affects `Development.md`; priorities affect `Roadmap.md`.

## VS Code / Tooling

Recommended VS Code extensions are listed in `.vscode/extensions.json`.

When adding or changing tooling, linters, formatters, frontend framework settings, backend development tools, or database tools:

- Update `.vscode/extensions.json` if an extension becomes required.
- Update `docs/Development.md`.
- Do not assume a tool is installed unless it is documented.

## Testing Guidelines

Backend tests use Django's runner. Add focused tests in the owning app, usually `backend/apps/stock/tests.py`. Frontend verification is `npm run build`.

## Commit & Pull Request Guidelines

Keep commits short and focused. PRs should include description, UI screenshots, migration notes, docs updated, and commands run.

## Agent-Specific Instructions

Apply changes directly and make the smallest safe change. Preserve user edits. Ask before destructive operations. Do not invent structure, remove features, hardcode model/API data, add accounting behavior, or leave docs outdated.
