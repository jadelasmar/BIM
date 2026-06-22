# Start Here

Read this file first before working on BIM Nexus.

## What BIM Nexus Is

BIM Nexus is an internal IT operations platform built for BIMPOS.

It currently focuses on:
- BIM Stock inventory
- stock availability
- receiving and delivery workflows
- operational records
- internal admin visibility

## What BIM Nexus Is Not

BIM Nexus is not:
- accounting software
- invoicing software
- payment software
- ticketing or Tasklogger replacement software

Accounting software owns official invoices, payments, and financial posting.

## Tech Stack

- Backend: Django
- Auth/admin/source of truth: Django
- API: Django REST Framework where React needs data
- Frontend: React, Vite, Tailwind CSS
- Frontend build output: `static/frontend/`
- Existing Django assets/theme: `static/bim/`
- Node.js role: frontend build tooling only

## Current Modules

Implemented or active:
- Command Center
- BIM Stock
- Operations shell
- Login/account setup
- Django admin

Visible but later:
- Clients
- Assets
- Knowledge Base
- Reports
- Forms/Documents

## Product Lifecycle

Product lifecycle in the current architecture:

1. Product is created as a catalogue definition.
2. ProductUnit records are created when stock is received.
3. Available ProductUnit records count as usable stock.
4. Delivery changes physical stock state and creates operational history.
5. Future stock movement records should become generated audit/history.

Do not store manual product quantity when it can be calculated from ProductUnit records.

## Current Focus

Current phase: Product Details refinement is complete.

Next task: `07 - Receiving Records`.

## Read Next

For every new task, read:

1. `docs/current-focus.md`
2. `docs/00-project-overview.md`
3. `docs/01-current-structure.md`
4. `docs/03-codex-rules.md`

Use these only when needed:

- `docs/02-roadmap.md` for future module direction
- `docs/04-ui-progress.md` for React/UI progress
- `docs/05-development-progress.md` for implementation progress
- `docs/archive/` for old prompts/session history

## Default Working Rule

Inspect first, keep scope focused, apply changes directly, run relevant checks, and update docs when behavior or architecture changes.
