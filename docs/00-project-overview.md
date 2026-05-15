# BIM Nexus Project Overview

This file explains the project goal and the business modules planned for BIM Nexus.

BIM Nexus is a Django-based internal IT operations platform.

BIM Nexus is not an accounting ERP, invoicing system, payment system, company ERP replacement, or Tasklogger replacement.

The project should stay modular. Each main business area should be built as its own Django app when it has its own workflow, but apps can still share data through clear relationships and APIs.

Example:
- BIM Stock owns products, inventory, SKU logic, and physical stock units
- Receiving / Delivery can select stock/products from BIM Stock
- Companies / Sites can be reused by deliveries, movements, assets, and reports
- Attachments can be reused by delivery scans, receiving scans, warranties, manuals, and documentation

## Current App

- BIM Stock

BIM Stock is the only implemented business app right now.

BIM Stock is used to manage inventory, products, quantities, suppliers, supplier cost, selling price, serial numbers, and stock status.

Main goals:
- check stock
- buy products from suppliers
- track issued/sold/delivered stock status without adding accounting logic
- track product quantity
- track supplier cost
- track client/selling price
- track serial numbers where needed
- keep stock status clear
- track minimum quantity needed in stock
- show what needs restocking

## Usage Goal

BIM Nexus is being built for internal company use first.

The main operational UI will move to React. Django remains the source of truth, and Django admin remains available for internal backend/admin management.

Build choices should support controlled multi-user internal use without overbuilding:
- keep data clean
- keep workflows simple
- use clear names
- use Django auth, groups, and permissions
- show users only modules they can access
- keep future reporting and exports in mind
- preserve admin readability for non-technical staff
- preserve SKU logic unless explicitly asked

## Planned Modules

1. Stock & Inventory
2. Stock Movement
3. Receiving / Delivery
4. Companies / Sites
5. Suppliers
6. Company Assets
7. Attachments
8. Knowledge Base / IT Docs
9. Reports

## Frontend Direction

React will be used for the main user interface. Figma screens should be inspected and mapped to Django models/APIs before implementation.

Initial React targets:
- login page
- protected Command Center/dashboard
- stock and inventory screens
- receiving and delivery screens
- companies/sites, suppliers, assets, knowledge base, and reports screens

Brand:
- name: BIM Nexus
- colors: black, white, orange
- style: professional internal dashboard
- layout: desktop-first, responsive for tablet/mobile

## Explicit Exclusions

Do not add:
- accounting workflows
- invoicing workflows
- payment workflows
- Tasklogger or ticketing workflows
