# BIM Nexus Project Overview

BIM Nexus is a Django-based internal IT operations platform.

It is not an accounting ERP, invoicing system, payment system, company ERP replacement, or Tasklogger replacement.

## Architecture Direction

- Django is the source of truth.
- Django admin must remain usable for non-technical staff.
- Django auth, groups, and permissions control access.
- Each major business workflow should become its own Django app when it has its own data and process.
- Apps may share data through clear relationships and APIs.
- React is the planned main operational UI, but no React app exists yet.

## Active Module

BIM Stock is the only implemented business module.

BIM Stock currently owns:
- product definitions
- physical stock units
- SKU generation
- suppliers
- supplier cost
- selling price
- serial numbers
- stock status
- product barcode search
- basic stock dashboard and list pages

## Current Product Scope

BIM Nexus focuses on:
- stock and inventory
- stock movement
- receiving and delivery operations
- suppliers
- companies and sites
- company assets
- internal IT documentation
- operational reporting

## Target Users

- internal IT teams
- operations staff
- warehouse/admin users
- management overview users

## Current UI

Implemented UI:
- Django-auth login page
- protected BIM Nexus Command Center at `/`
- BIM Stock dashboard at `/stock/`
- product list, product detail, and stock unit list pages
- Django admin

The current custom UI is Django templates and CSS. React should be introduced only after a focused setup/API session.

## Brand Direction

- Product name: BIM Nexus
- Subtitle: Internal IT Operations Platform
- Colors: black, white, orange accent
- Style: professional enterprise dashboard, desktop-first, responsive

## Frontend Direction

The main operational UI should be a modern enterprise SaaS/admin dashboard.

Use:
- dark collapsible left sidebar
- top navigation/header
- main content area
- compact KPI cards
- professional tables and forms
- reusable cards, buttons, badges, filters, and layout components

Avoid:
- flashy gradients
- gaming-style UI
- oversized marketing cards
- excessive empty spacing
- generic Bootstrap look

## Planned Modules

1. Command Center
2. Inventory / BIM Stock
3. Stock Movement
4. Receiving / Delivery
5. Companies / Sites
6. Suppliers
7. Company Assets
8. Knowledge Base
9. Reports
10. Settings

## Explicit Exclusions

Do not add:
- accounting workflows
- invoicing workflows
- payment workflows
- ticketing or Tasklogger replacement workflows
