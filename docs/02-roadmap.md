# Roadmap

This file tracks completed work, the current focus, and later planned features.

## Done

- Created Django project
- Created bim_stock app
- Added Product structure
- Added Brand
- Added Category
- Added Type
- Added ProductModel
- Added auto SKU generation
- Added Supplier
- Added ProductUnit
- Improved Product admin
- Improved ProductUnit admin
- Added ProductUnit client selling price tracking
- Added supplier purchase workflow defaults in ProductUnit admin
- Added simple selling workflow in ProductUnit admin
- Added simple BIM Stock dashboard
- Added custom BIM Stock product and stock unit pages
- Added product barcode visibility and search

## Current Focus

Move BIMPOS from stock-only Django templates toward a modular internal IT operations platform.

Detailed task sessions are listed in:
- docs/05-bim-stock-session-plan.md

## Next Steps

1. Add login/protected access using Django auth
2. Prepare groups/roles: Admin, Stock Manager, IT Support, Viewer
3. Add a module launcher that shows modules by permission
4. Plan and scaffold React without removing Django admin
5. Add API endpoints only where React needs them
6. Expand backend modules one session at a time

## Module Order

1. Login, roles, protected module launcher
2. Stock & Inventory hardening
3. Stock Movement audit trail
4. Companies / Sites
5. Receiving / Delivery
6. Suppliers improvements
7. Company Assets
8. Attachments
9. Knowledge Base / IT Docs
10. Reports structure
11. React operational UI
12. Figma-to-React implementation sessions as designs become available

## Later Enhancements

- printable receiving/delivery templates
- signed scan attachments
- dynamic dropdown filtering
- barcode label printing
- current stock exports
- Excel export
- PDF export
- dashboard charts
- backup/restore documentation
- ERP/POS integration only as read/write integration, not replacement accounting

## Out of Scope

- accounting
- invoices
- payments
- Tasklogger/ticketing
