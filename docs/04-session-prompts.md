# Codex Session Prompts

This file stores reusable prompts for focused project sessions.

## General Start Prompt

You are working on a Django project called BIMPOS.

Focus only on the requested task.
Keep replies short.
Do not explain every change.
Only summarize files changed, commands run, and blockers.

Read docs/00-project-overview.md, docs/01-current-structure.md, docs/02-roadmap.md, and docs/03-codex-working-rules.md before making changes.

Do not add accounting, invoicing, payment, or Tasklogger/ticketing features.

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
- damaged units

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
Polish BIM Stock UI.

Focus:
- dashboard
- product list
- stock list
- clear navigation

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

## Login / Module Launcher Session

Task:
Add protected BIMPOS access using Django auth.

Focus:
- login page
- secure logout
- protected pages
- groups: Admin, Stock Manager, IT Support, Viewer
- module launcher after login
- show/hide modules based on permissions

Do not build custom insecure authentication.
Do not remove Django admin.

## React Setup Session

Task:
Prepare React as the main operational UI.

Focus:
- inspect existing Django templates first
- choose a minimal frontend structure
- keep Django as source of truth
- use APIs only where React needs data
- preserve Django admin
- use BIMPOS black/white/orange branding

Do not rewrite the project blindly.
