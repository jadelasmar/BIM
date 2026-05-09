# BIM Stock Session Plan

Use one session per task.

Start every session with:

```text
Read docs/START-HERE.md first, then do this task:

[session task]
```

## Recommended Order

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
- pending

Task:
Add stock count display.

Focus:
- pending: available quantity per product
- pending: count ProductUnit where status is available and isactive is True
- pending: show count in Product admin list

Do not create custom frontend yet.

## Session 4: Product Pricing Fields

Status:
- pending

Task:
Add client price tracking.

Focus:
- pending: add selling price to Product or ProductUnit after checking best place
- pending: keep supplier cost on ProductUnit
- pending: run migrations
- pending: update admin

## Session 5: Purchase Workflow

Status:
- pending

Task:
Improve supplier purchase workflow.

Focus:
- pending: easy ProductUnit creation when buying stock
- pending: supplier
- pending: cost
- pending: purchase date
- pending: initial status available

Keep it simple in Django admin first.

## Session 6: Selling Workflow

Status:
- pending

Task:
Add selling workflow.

Focus:
- pending: mark ProductUnit as sold
- pending: sold date
- pending: client price if already added
- pending: prevent sold units from counting as available

Keep it simple in Django admin first.

## Session 7: Stock Dashboard

Status:
- pending

Task:
Create simple stock dashboard.

Focus:
- pending: total products
- pending: available units
- pending: sold units
- pending: damaged units
- pending: low stock products later

Use Django templates.

## Session 8: Custom Stock Pages

Status:
- pending

Task:
Create custom stock pages.

Focus:
- pending: product list
- pending: stock list
- pending: product detail
- pending: available units

Do not replace Django admin.

## Session 9: Barcode Support

Status:
- pending

Task:
Plan and implement barcode support.

Focus:
- pending: product barcode
- pending: future unit barcode
- pending: barcode search
- pending: avoid changing SKU logic unless needed

## Session 10: Stock UI Polish

Status:
- pending

Task:
Polish BIM Stock UI.

Focus:
- pending: improve dashboard layout
- pending: improve product list layout
- pending: improve stock list layout
- pending: add clear navigation
- pending: keep pages simple and usable

Do not work on other apps yet.
