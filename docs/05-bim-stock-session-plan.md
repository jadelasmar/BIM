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

Task:
Improve Product admin only.

Focus:
- better list display
- search by description, printed name, SKU, barcode
- filter by category, brand, active state
- readonly SKU and created date
- clean ordering

Do not change database models unless needed.

## Session 2: ProductUnit Admin Cleanup

Task:
Improve ProductUnit admin only.

Focus:
- list display for product, serial number, status, supplier, cost, purchase date, sold date
- search by serial number, product name, SKU
- filters for status, supplier, active state, dates
- readonly created date

Do not change Product model.

## Session 3: Stock Count Display

Task:
Add stock count display.

Focus:
- available quantity per product
- count ProductUnit where status is available and isactive is True
- show count in Product admin list

Do not create custom frontend yet.

## Session 4: Product Pricing Fields

Task:
Add client price tracking.

Focus:
- add selling price to Product or ProductUnit after checking best place
- keep supplier cost on ProductUnit
- run migrations
- update admin

## Session 5: Purchase Workflow

Task:
Improve supplier purchase workflow.

Focus:
- easy ProductUnit creation when buying stock
- supplier
- cost
- purchase date
- initial status available

Keep it simple in Django admin first.

## Session 6: Selling Workflow

Task:
Add selling workflow.

Focus:
- mark ProductUnit as sold
- sold date
- client price if already added
- prevent sold units from counting as available

Keep it simple in Django admin first.

## Session 7: Stock Dashboard

Task:
Create simple stock dashboard.

Focus:
- total products
- available units
- sold units
- damaged units
- low stock products later

Use Django templates.

## Session 8: Custom Stock Pages

Task:
Create custom stock pages.

Focus:
- product list
- stock list
- product detail
- available units

Do not replace Django admin.

## Session 9: Barcode Support

Task:
Plan and implement barcode support.

Focus:
- product barcode
- future unit barcode
- barcode search
- avoid changing SKU logic unless needed

## Session 10: Stock UI Polish

Task:
Polish BIM Stock UI.

Focus:
- improve dashboard layout
- improve product list layout
- improve stock list layout
- add clear navigation
- keep pages simple and usable

Do not work on other apps yet.
