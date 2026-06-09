# BIM Nexus Project Overview

BIM Nexus is a Django-based internal IT operations platform.

It is not an accounting ERP, invoicing system, payment system, company ERP replacement, or Tasklogger replacement.

## Architecture Direction

- Django is the backend, source of truth, auth layer, admin, and API provider.
- BIM Nexus is the product/platform name shown to users.
- The current internal Django project package is `bim`; do not rename it only to match the product name.
- Django admin must remain usable for non-technical staff.
- Django auth, groups, and permissions control access.
- Each major business workflow should become its own Django app when it has its own data and process.
- Each Django app should appear in BIM Nexus as a clear module, such as BIM Stock.
- Apps may share data through clear relationships and APIs.
- React is the main operational frontend for the protected Command Center.
- Tailwind CSS is the planned frontend styling system.
- Node.js should be used only as frontend build tooling, not as a backend for BIM Nexus.

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
- email-or-username login using Django auth
- admin-generated manual setup links for internal users to enter first name, last name, username, and password
- blank setup usernames default to the email name before `@`
- protected BIM Nexus Command Center at `/`
- React/Tailwind Command Center app shell with sidebar and operational dashboard
- BIM Stock dashboard at `/stock/`
- product list, product detail, and stock unit list pages
- Django admin

The Command Center is now React/Tailwind. Login, Django admin, and existing BIM Stock pages still use Django templates.

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
