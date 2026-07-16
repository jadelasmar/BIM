# BIM Nexus

Internal IT operations / inventory management platform for BIMPOS. Tracks physical stock units (by serial number) through their full lifecycle — receiving, delivery, reservation, issuing, repair, and client returns — with a permanent audit trail of every status change.

## Stack

- **Backend:** Django 6, Django REST Framework, SQLite (dev). Lives in `backend/`.
- **Frontend:** React 19 + Vite, Tailwind CSS. Lives in `frontend/src/`.
- **Integration:** Django serves a single shell template (`bim/react_app.html`) with server-injected `initial_data` (permissions, nav, KPIs, current path). React hydrates on top and handles client-side routing based on `initialData.currentPath`. All *other* Django URLs (see `backend/apps/core/urls.py`) intentionally point at the same `module_launcher` view — the URL exists for direct linking/refresh, but the view switching itself happens in React, not Django. After the initial load, all reads/writes go through the REST API under `/api/stock/`.

## Repo layout

```
backend/
  bim/                  # Django project settings, root urls, asgi/wsgi
  apps/
    core/                # module_launcher view, ui_config.py (nav/icon/tone tokens), templates
    accounts/            # auth: login, password setup, username-or-email backend
    stock/                # the actual domain app
      models.py           # Product, ProductUnit, and one Record+Item pair per workflow
      constants.py         # permission string constants (single source of truth for perms)
      roles.py             # Administrator / IT Support / Viewer group definitions
      services.py           # ALL state-changing business logic lives here
      selectors.py           # read-only queries for dashboard/summary data
      serializers.py           # DRF serializers, call into services.py to mutate
      api_views.py               # thin DRF views: permission check + delegate to serializer/service
      api_urls.py                 # /api/stock/... routes
      admin.py, tests.py
frontend/
  src/
    routes/AppRouter.jsx   # ~7,600 lines, ~90 components — the entire client-side app (see below)
    components/ui/          # shared primitives: Button, Card, Badge, Input, SearchBar, EmptyState
    components/common/Icon.jsx
    constants/               # icons.js, statusStyles.js, uiRegistry.js (tone/label tokens, mirrors backend ui_config.py)
    pages/auth/AuthPages.jsx  # login + password setup (server-rendered form actions, not API-driven)
    hooks/useTheme.js
    utils/formatters.js
```

## The domain model

`Product` is a catalogue entry (category + brand + model, generates its own SKU). `ProductUnit` is one physical, serialized item — the thing that actually moves through statuses: `available → reserved/issued/repair/sold`, and back. Every workflow has a `*Record` (the transaction header: `ReceivingRecord`, `DeliveryRecord`, `ReservationRecord`, `IssueRecord`, `RepairRecord`, `ClientReturnRecord`) and a `*Item` (the line linking that record to specific `ProductUnit`s). Every record type auto-generates a sequential human-readable number per year (`RCV-2026-0001`, `DLV-2026-0001`, etc.) in its own `save()`.

`StockMovement` is an append-only audit log. Every status transition on a `ProductUnit`, anywhere in the app, must create a corresponding `StockMovement` row via `services.create_stock_movement()`. This is not optional bookkeeping — it's how the product detail page's movement history and the audit trail work. If you add a new way to change a unit's status, add the matching movement entry.

## Critical conventions — do not deviate

1. **Never mutate `ProductUnit.status` outside `services.py`.** Every workflow transition (reserve, issue, repair, return, cancel, resolve) is a function in `services.py` wrapped in `@transaction.atomic`, using `select_for_update()` to lock the units involved, validating current state before transitioning, and writing a `StockMovement`. `api_views.py` and `serializers.py` should only ever call into these functions, never set `.status` and `.save()` directly. The one exception is direct manual add/edit of a `ProductUnit` via `ProductUnitListCreateAPIView`/`ProductUnitDetailAPIView`, which still logs `TYPE_MANUAL_ADD`/`TYPE_MANUAL_UPDATE` movements itself.
2. **Permission constants, not raw strings.** All permission checks go through `stock/constants.py` (e.g. `stock_constants.ADD_DELIVERY_RECORD`), checked via `_require_perm()` in `api_views.py`. Most write operations require two permissions: the record-type permission (e.g. `ADD_DELIVERY_RECORD`) *and* `CHANGE_PRODUCT_UNIT`, since they mutate units too. Follow this pairing when adding new write endpoints.
3. **The six workflow records follow one shared shape.** Create → (optional) correct header → cancel/release/return/resolve. Each has near-identical validation logic (only untouched units in the expected state can be released/returned/resolved — see `_reservation_item_can_be_released`, `_issue_item_can_be_returned`, `_repair_item_can_be_resolved`, `_delivery_unit_can_be_corrected` in `services.py`). This repetition is deliberate parallelism, not an accident — when fixing a bug in one workflow's guard logic, check whether the same bug exists in the other five.
4. **`AppRouter.jsx` is one file on purpose, for now.** `backend/apps/stock/tests.py` reads this file's source directly (`REACT_APP_SOURCE`) to assert on UI wiring. Don't split it up without first checking what those tests actually assert and updating them — this file has been flagged as a maintainability risk and is a planned refactor, but it needs to happen deliberately, not as a side effect of an unrelated change.
5. **UI tokens are duplicated by design, keep them in sync.** `backend/apps/core/ui_config.py` (icon/label/tone per feature key) and `frontend/src/constants/uiRegistry.js` / `statusStyles.js` mirror each other. The backend sends rendering hints in `initial_data`; the frontend has its own copy for client-rendered pages that don't get fresh server data. If you add a new module or status, update both sides.
6. **"Coming later" is intentional, not broken.** Assets and Knowledge Base modules are stubbed everywhere (`disabled_ui_item(...)`, `enabled: False`, `href: None`) on purpose — they're future modules, not missing features. Don't build them out without an explicit ask.

## Known state / open issues

- **Frontend is a single large file.** `AppRouter.jsx` (~7,600 lines / ~90 components) contains every page in the app. Functionally complete, but a refactor into per-module files is planned — see convention #4 above before touching it.
- **No CI/lint config committed yet.** No `.flake8`, `pyproject.toml` formatter config, `.eslintrc`, or `.prettierrc` currently in the repo. Match the existing style in the file you're editing rather than introducing a new one unprompted.
- **Git hygiene:** work in this repo has previously accumulated as uncommitted changes for long stretches. Commit logically-scoped changes as you go rather than leaving a large uncommitted diff.

## Running it locally

```
# backend (from backend/)
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# frontend (from frontend/)
npm install
npm run dev
```

Django needs `BIM_VITE_DEV_SERVER` set (see `backend/bim/settings.py`) to point at the Vite dev server for hot reload during development; without it, the shell template won't pick up live frontend changes.

## When making changes

- New workflow transitions → add the function to `services.py` following the existing pattern (atomic, `select_for_update`, validate-then-mutate, `create_stock_movement` call), then wire a thin view/serializer on top.
- New permissions → add to `stock/constants.py` first, wire into `roles.py` group definitions if it should be included in Administrator/IT Support/Viewer.
- New frontend page → check `constants/uiRegistry.js` and `components/ui/` first; reuse the existing primitives (`Card`, `Badge`, `Button`, `SearchBar`, `EmptyState`) rather than building new ones, to keep the design consistent.
- Before any structural refactor (especially `AppRouter.jsx`), check `apps/stock/tests.py` for source-file assertions that would break.

## Workflow: human-in-the-loop testing

The user tests changes manually in the browser and reports back specific bugs or feedback — this is not a fully autonomous pipeline.

- Keep changes scoped to what was asked. Avoid drive-by refactors or "while I'm here" fixes, even if they seem correct — they make the user's manual review harder and obscure what actually changed for a given fix. This does not override convention #3 above: if a reported bug is in one workflow's guard logic (reserve/issue/repair/return/cancel/resolve), check the other five workflows for the same bug as usual, since that's a documented project convention, not scope creep. Just call out clearly in the summary which files changed and why, so a multi-file fix is still easy to review.
- For a small, well-defined bug fix (one component, one endpoint, one visual issue), it's fine to skip the full `superpowers` spec/plan flow and just make the fix directly, run the relevant backend/frontend check, and report what changed.
- For a new feature, a schema change, or anything touching multiple files/apps, use `superpowers:subagent-driven-development` or `superpowers:executing-plans` as usual — the size of the change decides which path applies, not habit.
- Don't write new automated tests for every one-line fix the user reports; match test effort to the size of the change, per existing testing guidelines in `AGENTS.md`.
- After a fix, state plainly what to test and how (e.g. "reload the receiving page and confirm the cancel button now works for IT Support users") so the user's manual pass is fast and targeted.
- If a reported bug turns out to require a larger or riskier change than described, say so and propose the plan/spec path before proceeding, rather than quietly expanding scope.
