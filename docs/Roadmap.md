# Roadmap

This roadmap documents product direction, not implementation history.

## Completed / Active

- Command Center
- Inventory list
- Product Details
- Add Product
- Receive Stock using `ReceivingRecord`
- Add Unit
- Create Delivery
- Delivery records API
- Delivery Records list frontend
- Delivery Record detail frontend
- Delivery record edit/cancel correction workflow
- Receiving records backend API
- Receiving Records list frontend
- Receiving Record detail frontend
- Receiving record edit/cancel correction workflow
- StockMovement operational ledger foundation
- Reservation records workflow
- Issue and return-from-issue workflow
- Repair workflow
- Client return workflow using sold-to-available and sold-to-repair transitions
- Removal workflow (`RemovalRecord`, `RMV-YYYY-####`): permanently removes units from stock as damaged, lost, stolen, written off or other; create-only, no undo
- Client Upgrade workflow (`ClientUpgradeRecord`, `/operations/upgrades/...`): tracks which clients still need a software upgrade and which are done; it never touches stock units
- Product edit (`/inventory/products/<id>/edit/`) and Product Groups (`/inventory/groups/`)
- Global search across products, groups, units, suppliers, clients and every record type, permission-gated
- Record edit history (`RecordChange`) shown on detail pages, plus the per-unit journey from `StockMovement`
- Office-ready ProductUnit status vocabulary
- First office testing/deployment checklist
- Supplier and Client master data modules
- Django admin for stock and users
- Login and password setup
- Dark/light theme
- React/Vite/Tailwind frontend shell
- Command Center as a module dashboard: Needs Attention list plus one summary card per module, fed by per-module dashboard providers (`apps/core/dashboard.py`)
- Inventory Stock Units view (every serial with where it is now, editable) and CSV export of products or units
- Operations page grouped by purpose with live counts and its open work

## Current Product Focus

First internal office testing is complete and passed. BIM Nexus is moving to shared use by several office users at once; the focus is stability, backups and keeping the docs current before reports or secondary modules.

Receiving and delivery records now have operational create/list/detail workflows under `/operations/...`. Manual Add Unit remains a direct stock unit workflow under inventory.

StockMovement now records receiving, receiving cancellation, delivery, delivery cancellation, reservation, reservation release, issue, issue return, repair creation, repair resolution, client return creation, manual Add Unit, and direct product-unit status update movements going forward. The ProductUnit status set is available, reserved, issued, sold, repair, removed and inactive (`removed` is the permanent write-off status set by a Removal Record; `inactive` is only set by cancelling a receiving record or resolving a repair as deactivated). Client Return v1 moves sold units to available or repair without adding a permanent returned status.

## Near-Term Modules

- Better stock history views
- Broader office stock polish around operational usability
- Move uploaded media (`/media/`) behind authentication and include `backend/media/` in deploy backups

## Future Modules

- Advanced supplier/client relationship views
- Assets
- Knowledge Base
- Reports
- Forms/Documents
- Notifications
- A dedicated audit-log browser (record history and stock movements are recorded and shown per record/unit today; there is no system-wide log page)
- Users/Roles operational UI

## Explicit Non-Goals

BIM Nexus is not:

- accounting software
- invoicing software
- payment software
- financial posting software
- public signup software
- ticketing or Tasklogger replacement software

Accounting software owns official invoices, payments, and financial posting.
