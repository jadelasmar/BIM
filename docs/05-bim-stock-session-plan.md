# BIM Stock Session Plan

This file tracks the step-by-step BIM Stock implementation sessions.

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
