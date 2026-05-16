# Codex Session Prompts

Reusable prompts for focused BIM Nexus work.

## General Start Prompt

```text
You are working on BIM Nexus, a Django-based internal IT operations platform.

Read:
- docs/00-project-overview.md
- docs/01-current-structure.md
- docs/02-roadmap.md
- docs/03-codex-working-rules.md
- docs/current-focus.md

Focus only on the requested task.
Keep replies short.
Summarize only files changed, important decisions, commands run, and blockers.
Do not add accounting, invoicing, payment, or ticketing/Tasklogger replacement features.
```

## Documentation Review Session

```text
Review docs against the current codebase.
Inspect models, admin, views, URLs, templates, and roadmap.
Update docs so they describe the real current implementation.
Do not invent future features as completed.
```

## Product Admin Session

```text
Improve Product admin only.

Focus:
- list_display
- search_fields
- list_filter
- readonly sku and crdate
- clean ordering

Do not change database models unless necessary.
```

## ProductUnit Admin Session

```text
Improve ProductUnit admin only.

Focus:
- serial number
- product
- supplier
- status
- cost
- selling price
- active flag
- admin list/search/filter

Run migrations only if models change.
```

## BIM Stock UI Session

```text
Polish BIM Stock Django-template UI.

Focus:
- dashboard
- product list
- product detail
- stock unit list
- clear navigation back to Command Center

Do not replace Django admin.
Do not introduce React in this session.
```

## Login UI From Figma Session

```text
Implement the BIM Nexus login UI from the provided Figma URL or screenshot.

Focus:
- templates/registration/login.html
- black, white, orange accent branding
- professional internal operations style
- responsive layout
- keep Django auth form behavior intact

Do not change authentication logic.
Do not add React unless this is explicitly part of a React setup session.
```

## Command Center Session

```text
Improve the BIM Nexus Command Center.

Focus:
- operational KPI cards
- quick actions
- module shortcuts
- recent activity
- permission-aware links

Use real BIM Stock data where available.
Show pending modules as pending; do not invent models.
```

## Stock Hardening Session

```text
Harden BIM Stock behavior.

Focus:
- permissions
- stock statuses
- admin clarity
- SKU preservation
- existing data compatibility

Do not rename fields or statuses casually.
```

## Stock Movement Session

```text
Add stock movement audit history.

Focus:
- movement type
- Product and ProductUnit links where useful
- quantity
- user
- date/time
- notes/reason

No accounting logic.
```

## React Setup Session

```text
Prepare React as the main operational UI.

Focus:
- inspect current Django templates first
- add a minimal frontend structure
- keep Django as source of truth
- preserve Django admin
- add APIs only where React needs data
- use BIM Nexus black/white/orange branding
- create reusable layout/components for sidebar, topbar, cards, tables, forms, badges, filters, and page headers
- keep the UI compact, professional, desktop-first, and responsive

Do not rewrite the project blindly.
```
