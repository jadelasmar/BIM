# Codex Session Prompts

## General Start Prompt

You are working on a Django project called BIM.

Focus only on the requested task.
Keep replies short.
Do not explain every change.
Only summarize files changed, commands run, and blockers.

Read docs/00-project-overview.md, docs/01-current-structure.md, docs/02-roadmap.md, and docs/03-codex-working-rules.md before making changes.

## Product Admin Session

Task:
Improve Product admin only.

Focus:
- list_display
- search_fields
- list_filter
- readonly sku and crdate
- clean ordering

Do not change database models unless necessary.

## ProductUnit Session

Task:
Improve ProductUnit model/admin.

Focus:
- serial number
- product
- supplier
- status
- cost
- active flag
- admin list/search/filter

Run migrations if models are changed.

## Stock Count Session

Task:
Add stock count display.

Focus:
- available quantity per product
- count ProductUnit where status is Available and isactive is True
- show count in admin list

Do not create custom frontend yet.

## Dashboard Session

Task:
Create simple dashboard page.

Focus:
- total products
- available units
- sold units
- inactive products

Use Django templates.

## Barcode Session

Task:
Plan and implement barcode support.

Focus:
- product barcode
- future unit barcode
- avoid changing SKU logic unless needed

## UI Session

Task:
Create custom user-facing pages.

Focus:
- login
- dashboard
- product list
- stock list

Do not replace Django admin.

## Receiving / Delivery Session

Task:
Create Receiving / Delivery app.

Focus:
- printable document template
- product lines
- company
- receiver
- deliverer
- date
- notes

Keep it simple first.
Do not connect it to accounting or POS yet.
