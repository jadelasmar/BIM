# BIMPOS Session Plan

This file tracks step-by-step BIMPOS implementation sessions.

Use one session per task.

Start every session with:

```text
Read docs/START-HERE.md first, then do this task:

[session task]
```

## Completed BIM Stock Order

1. Product admin cleanup
2. ProductUnit admin cleanup
3. Stock count display
4. Product pricing fields
5. Purchase workflow
6. Selling workflow
7. Stock dashboard
8. Custom stock pages
9. Barcode support
10. Stock UI polish

## Before Wider Use

Before BIM Stock is used by more people:
- add user roles and permissions
- add audit history for stock changes
- confirm backup plan
- review security settings
- test common workflows with real data
- add exports for stock reports

## Next BIMPOS Order

Work one module/session at a time:

1. Login, roles, and protected Command Center
2. Stock & Inventory hardening for BIMPOS statuses and permissions
3. Stock Movement audit trail
4. Companies / Sites
5. Receiving / Delivery
6. Suppliers improvements
7. Company Assets
8. Reusable Attachments
9. Knowledge Base / IT Docs
10. Reports structure
11. React setup and API bridge
12. Figma-to-React screen implementation

Do not add accounting, invoicing, payment, or Tasklogger/ticketing features.

## Session 11: Login, Roles, and Command Center

Status:
- done

Task:
Add proper BIMPOS login and protected access.

Focus:
- done: use Django auth as source of truth
- done: create or prepare groups: Admin, Stock Manager, IT Support, Viewer
- done: protect operational pages
- done: add secure logout
- done: add BIM Nexus Command Center after login
- done: show/hide modules based on permissions
- done: keep Django admin usable

Do not build custom insecure authentication.

## Session 12: Stock & Inventory Hardening

Status:
- pending

Task:
Align BIM Stock with BIMPOS stock requirements without duplicating models.

Focus:
- inspect existing Product and ProductUnit first
- preserve SKU logic
- review stock statuses before changing choices
- add missing status values only if needed
- keep admin readable
- prepare API needs for React

Avoid unrelated refactors.

## Session 13: Stock Movement Audit Trail

Status:
- pending

Task:
Add stock movement history as an audit trail.

Focus:
- movement type
- product
- stock unit where applicable
- quantity
- user
- date/time
- notes/reason
- related company/site where useful after those models exist

No accounting logic.

## Session 14: Companies / Sites

Status:
- pending

Task:
Add shared companies, sites/branches, contacts, addresses, notes, and active state.

Focus:
- reusable by delivery, receiving, stock movement, assets, and reports
- clear admin lists/search/filters
- avoid hardcoding one company only

## Session 15: Receiving / Delivery

Status:
- pending

Task:
Add dedicated receiving and delivery modules.

Focus:
- receiving note number
- delivery note number
- supplier or company/site links
- receiver/deliverer/contact
- date
- item lines
- notes
- linked stock/products
- printable forms later
- signed scan attachments later

Do not merge into generic documents.
Do not add invoices or payments.

## Session 16: Company Assets

Status:
- pending

Task:
Add company-owned equipment tracking separate from stock inventory.

Focus:
- asset name/type
- brand/model
- serial number
- asset tag/barcode
- assigned employee/user
- department
- location
- status
- purchase/warranty dates if known
- notes
- attachments later

Stock units remain inventory. Company assets are internal equipment in use.

## Session 17: Attachments

Status:
- pending

Task:
Add reusable shared attachments.

Focus:
- file
- title
- notes
- uploaded by
- uploaded date
- related record
- admin inlines where useful

## Session 18: Knowledge Base / IT Docs

Status:
- pending

Task:
Add internal IT documentation.

Focus:
- title
- category
- tags
- content/body
- attachments
- active/inactive
- created/updated audit fields

This is documentation only, not ticketing.

## Session 19: Reports

Status:
- pending

Task:
Prepare report structure.

Focus:
- current stock
- available stock
- damaged stock
- delivery history
- receiving history
- stock movement history
- supplier history
- company assets
- company/site history
- structure for Excel/PDF exports later

## Session 20: React Operational UI

Status:
- pending

Task:
Introduce React for the main BIMPOS operational UI.

Focus:
- inspect current Django pages first
- keep Django admin
- add protected routes/pages
- use real APIs where data exists
- build reusable components
- use BIMPOS black/white/orange branding
- desktop-first responsive design

Implement Figma screens only after inspecting the provided designs.

## Session 1: Product Admin Cleanup

Status:
- done

Task:
Improve Product admin only.

Focus:
- done: better list display
- done: search by description, printed name, SKU, barcode
- done: filter by category, brand, active state
- done: readonly SKU and created date
- done: clean ordering
- done: optimize related category type and brand lookups in Product admin

Do not change database models unless needed.

## Session 2: ProductUnit Admin Cleanup

Status:
- done

Task:
Improve ProductUnit admin only.

Focus:
- done: list display for product, serial number, status, supplier, cost, purchase date, sold date
- done: search by serial number, product name, SKU
- done: filters for status, supplier, active state, dates
- done: readonly created date
- done: optimize related product and supplier lookups in ProductUnit admin

Do not change Product model.

## Session 3: Stock Count Display

Status:
- done

Task:
Add stock count display.

Focus:
- done: available quantity per product
- done: count ProductUnit where status is available and isactive is True
- done: show count in Product admin list

Do not create custom frontend yet.

## Session 4: Product Pricing Fields

Status:
- done

Task:
Add client price tracking.

Focus:
- done: add selling price to ProductUnit after checking best place
- done: keep supplier cost on ProductUnit
- done: run migrations
- done: update admin

## Session 5: Purchase Workflow

Status:
- done

Task:
Improve supplier purchase workflow.

Focus:
- done: easy ProductUnit creation when buying stock
- done: supplier
- done: cost
- done: purchase date
- done: initial status available

Keep it simple in Django admin first.

## Session 6: Selling Workflow

Status:
- done

Task:
Add selling workflow.

Focus:
- done: mark ProductUnit as sold
- done: sold date
- done: client price if already added
- done: prevent sold units from counting as available

Keep it simple in Django admin first.

## Session 7: Stock Dashboard

Status:
- done

Task:
Create simple stock dashboard.

Focus:
- done: total products
- done: available units
- done: sold units
- done: damaged units
- done: low stock products kept for later because minimum stock is not tracked yet

Use Django templates.

## Session 8: Custom Stock Pages

Status:
- done

Task:
Create custom stock pages.

Focus:
- done: product list
- done: stock list
- done: product detail
- done: available units

Do not replace Django admin.

## Session 9: Barcode Support

Status:
- done

Task:
Plan and implement barcode support.

Focus:
- done: product barcode
- done: future unit barcode planned as a later ProductUnit model change
- done: barcode search
- done: avoid changing SKU logic unless needed

## Session 10: Stock UI Polish

Status:
- done

Task:
Polish BIM Stock UI.

Focus:
- done: improve dashboard layout
- done: improve product list layout
- done: improve stock list layout
- done: add clear navigation
- done: keep pages simple and usable

Do not work on other apps yet.
