# Module Dashboard (Command Center redesign)

Date: 2026-10-21. Status: approved by the user for implementation ("plan and check if it needs fixing then start it").

## Goal

The Command Center today is stock-only: a stock status chart, four stock KPI cards, a System Overview row and Recent Activity. BIM Nexus is getting modules beyond stock (Assets, Knowledge Base, licenses, ...), so the dashboard becomes a per-module overview that new modules plug into, with what needs action shown first.

## Layout

1. **Needs Attention**: one list of things someone has to act on, from every module the user can see. Each row is a count, a sentence and a link to the filtered list behind it. Only rows with a count above zero are shown; with none, a single "All clear" line.
2. **Module summary cards**: one card per module the user can see. Each card has a title and icon, 2-4 headline numbers (each clickable) and an "Open" link. Phone: one column; tablet: two; wide desktop: three.
3. **Recent Activity**: unchanged.

Removed from the Command Center (their numbers move into the cards, nothing is lost): the Stock Status Breakdown chart, the four KPI cards and the System Overview row.

## Content at launch (existing data only)

| Card | Permission | Numbers |
|---|---|---|
| Stock | can view stock | Available of total in stock (with a reserved / issued / repair bar), Products, Low stock, Out of stock |
| Operations | can use operations | Active reservations, Active temporary assignments, Open repairs, Receiving last 30 days, Deliveries all-time |
| Clients & Suppliers | view client / view supplier | Clients, Suppliers, Clients needing an upgrade |

| Needs Attention row | Permission | Link |
|---|---|---|
| Products out of stock | can view stock | `/inventory/?stock=out` |
| Products low on stock | can view stock | `/inventory/?stock=low` |
| Temporary assignments overdue | view issue record | `/operations/pending/` |
| Repairs with no supplier | view repair record | `/operations/pending/` |
| Repairs open more than 30 days | view repair record | `/operations/repairs/` |
| Reservations held more than 30 days | view reservation record | `/operations/reservations/` |
| Client upgrades past their planned date | view client upgrade record | `/operations/upgrades/?filter=overdue` |

Order: red ("out of stock", "overdue") before orange.

## How modules plug in

- `backend/apps/core/dashboard.py`: `build_dashboard(user)` runs every function in `DASHBOARD_PROVIDERS` and returns `{"attention": [...], "sections": [...]}`.
- Each module owns its providers. Stock ones live in `backend/apps/stock/dashboard.py`: `stock_dashboard`, `operations_dashboard` and `clients_dashboard`. Each takes the user and returns `{"section": {...} | None, "attention": [...]}`, already filtered by that user's permissions.
- New selectors in `apps/stock/selectors.py`: `long_open_repair_count`, `long_held_reservation_count`, `overdue_client_upgrade_count` and `client_upgrade_needed_count`.
- The payload gains `dashboard`, built only for the Command Center (`/` and `/api/command-center/`), so other pages do no extra queries. The existing 60-second refresh keeps it live.
- Standing rule (added to CLAUDE.md): a new module adds a dashboard provider (its card plus its Needs Attention rows), the same way it adds a global search group.

## Frontend

- `CommandCenter` renders `NeedsAttention` and `ModuleSummaryCards` from `dashboard`, then `RecentActivity`.
- `StockStatusChart` and `Overview` are deleted. Their only use was the Command Center, and the Stock card carries the status bar.
- The Client Upgrades list reads `?filter=` (e.g. `overdue`) to open on that chip, so the attention link lands on the right rows.

## Plan check (problems found in the first draft and how they were fixed)

1. **Quick-actions row dropped.** The first draft added one. `tests.py` (`test_command_center_layout_removes_duplicate_panels`) records that a quick-actions panel was removed on purpose as a duplicate of the Operations page, and Scan already lives in the top bar.
2. **No information removed.** The first draft moved the stock chart to Inventory, but Inventory already has Total / Available / Reserved / Issued / Repair cards, so that would duplicate it. Every number from the old KPI cards, chart and System Overview now appears on a card instead (see table). AGENTS.md says not to remove features.
3. **No extra queries on every page.** Every page's initial data is built by the same function, so the dashboard is built only when the Command Center is shown.
4. **The existing payload stays.** `kpis`, `overview`, `stockStatusChart`, `modules` and `quickActions` are asserted by about 15 backend tests and stay in the payload unchanged. Removing them is a separate clean-up.
5. **Links must land on the matching rows.** Client Upgrades had no URL filter; one is added. Overdue assignments and vendorless repairs already sort first on the Pending page, so they link there.
6. **Permission per row, not per card.** A user who can view repairs but not issues sees only the repair rows.
7. **UI tokens.** Cards reuse the existing tokens (`inventory`, `operations`, `clients`, `out_of_stock`, `low_stock`, `pending_actions`, `repair_records`, `reservation_records`), so `ui_config.py` and `uiRegistry.js` need no new keys and stay in sync.

## Out of scope

Assets, Knowledge Base and other new modules (separate plans); notifications; removing the old payload keys.

## Verification

- `python manage.py check`, `npm run build`.
- Backend check of `build_dashboard` for an admin, a viewer and a user with only repair access.
- Screenshots of the Command Center at phone and desktop width.
- Tests: focused backend tests in `apps/stock/tests.py` for provider permissions and counts. Per CLAUDE.md, the suite runs only when asked.
