# UI Progress

## Current Phase

Command Center is complete for Phase 1.

## Finalized For Current Phase

- Login page and password setup flow.
- Sidebar shell with Command Center, BIM Stock, and Operations for normal users.
- Administration appears only for admin-capable users and links to Django admin.
- Global topbar includes theme toggle, Quick Add, and logout/user controls.
- Theme support for dark and light mode.
- Command Center dashboard.
- BIM Stock list page.
- Add Product page.
- Receive Stock page.
- Create Delivery page.
- Operations hub page.

## Command Center Status

- Navigation links are protected and route correctly.
- Theme toggle is available in the global topbar for authenticated users and persists through `bim-nexus-theme`.
- Command Center data auto-refreshes every 60 seconds through `/api/command-center/`.
- Administration is hidden from normal users/viewers.
- Quick Add is a dropdown with Add Product, Receive Stock, Create Delivery, and disabled Add Supplier.
- KPI cards use backend data where available.
- Recent Activity uses DeliveryRecord data when available and ProductUnit fallback data for receiving until ReceivingRecord exists.
- References use operational display formats such as `RCV-YYYY-0001` and `DLV-YYYY-0001`.
- Low Stock cards show product name, category, available quantity, and reorder threshold.
- Recent Receiving rows link to product detail pages; Recent Delivery rows carry future detail metadata until delivery detail pages exist.
- Empty states use clean production wording.
- Pending modules are muted and marked `Coming later`.
- Command Center avoids accounting, invoice, payment, and support-ticket concepts.

## Next UI Focus

06 - Product Details.
