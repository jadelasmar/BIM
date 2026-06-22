# Project Overview

## Product

BIM Nexus is an internal IT operations platform built for BIMPOS.

The active implemented business module is BIM Stock.

## Direction

BIM Nexus should help internal IT and operations teams track:
- products
- physical stock units
- receiving
- delivery
- operational history
- suppliers
- clients
- assets later
- internal documents later
- reports later

## Explicit Exclusions

BIM Nexus is not:
- accounting software
- invoicing software
- payment software
- financial posting software
- public sign-up software
- ticketing or Tasklogger replacement software

Accounting software owns official invoices, payments, and financial records.

## Architecture Direction

- Django is the backend, auth layer, admin, API provider, and source of truth.
- Django admin must remain usable for non-technical staff.
- Django auth, groups, and permissions control access.
- React/Vite/Tailwind is the main operational UI direction.
- Node.js is frontend build tooling only.
- Major business workflows should become focused Django apps/modules when they have their own data and process.

## Core Inventory Model

- `Product` is a product definition.
- `ProductUnit` is one physical stock item.
- Product quantity should be calculated from active ProductUnit records.
- SKU is auto-generated and should not be changed casually.
- Soft delete uses `isactive`.

## Operational Records

Receiving records are internal stock-entry records, not invoices.

Delivery records are internal stock-exit/dispatch records, not invoices.

Stock movement should become generated audit/history, not the main daily workflow except for adjustments.

Operational numbers should use readable formats:
- `RCV-YYYY-0001`
- `DLV-YYYY-0001`
- `DOC-YYYY-0001`
- `AST-YYYY-0001` where needed

## Brand

- Product name: BIM Nexus
- Built for: BIMPOS
- Subtitle: Internal IT Operations Platform
- Visual style: black, white, orange accent
- UI style: compact enterprise dashboard
