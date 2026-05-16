# Roadmap

This roadmap separates completed work from planned work. Do not mark future modules as complete until models, admin, views, and checks exist.

## Completed

- Django project `bim`
- Django app `bim_stock`
- Product hierarchy: `Type`, `Category`, `Brand`, `ProductModel`, `Product`
- Auto-generated SKU on `Product`
- Supplier model
- ProductUnit model for physical stock items
- Product barcode field and search
- ProductUnit cost, selling price, purchase date, sold date, notes, active flag
- Product admin improvements
- ProductUnit admin improvements
- Supplier admin
- Purchase defaults in ProductUnit admin
- Mark selected ProductUnits as sold admin action
- BIM Stock dashboard
- Product list, product detail, and stock unit list pages
- Django-auth login/logout
- Protected pages
- Role/group preparation
- BIM Nexus Command Center
- BIM Nexus branding update in current UI

## Current Focus

BIM Stock is the active module. The project is moving from stock-only Django templates toward a modular internal IT operations platform.

Current UI work should focus on:
- login screen alignment with Figma
- Command Center refinement
- preserving Django admin usability

## Immediate Next Steps

1. Implement the Figma-directed login UI in the existing Django login template.
2. Harden BIM Stock permissions and status behavior without changing SKU logic.
3. Add stock movement audit history.
4. Plan API endpoints only where the frontend needs real data.
5. Introduce React in a dedicated setup session, not as an incidental change.

## Planned Module Order

1. Command Center
2. Inventory / BIM Stock hardening
3. Stock Movement audit trail
4. Companies / Sites
5. Receiving / Delivery
6. Suppliers improvements
7. Company Assets
8. Reusable Attachments
9. Knowledge Base / IT Docs
10. Reports
11. React operational UI and API bridge
12. Figma-to-React implementation

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

## Out of Scope

- accounting
- invoices
- payments
- Tasklogger or ticketing replacement
