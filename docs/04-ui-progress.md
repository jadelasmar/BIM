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
- Product Details page with stock-unit register, product overview, activity sidebar, and permission-aware workflow actions.
- Receive Stock page.
- Create Delivery page.
- Operations hub page.

## Command Center Status

- Navigation links are protected and route correctly.
- Theme toggle is available in the global topbar for authenticated users and persists through `bim-nexus-theme`.
- Topbar includes Refresh, Quick Add, user controls, logout, and global theme toggle.
- Command Center data auto-refreshes every 60 seconds through `/api/command-center/`.
- Administration is hidden from normal users/viewers.
- Quick Add is a dropdown with Add Product, Receive Stock, Create Delivery, disabled Add Supplier, and disabled Add Client.
- KPI cards use backend data where available.
- KPI cards are clickable shortcuts to BIM Stock and stock-filtered inventory views.
- System Overview cards route to Suppliers, Receiving Records, Delivery Records, and Clients placeholders where full modules are not ready.
- The large Quick Actions panel was removed; Quick Add remains in the topbar.
- The duplicate bottom Low Stock Alerts panel was removed; low stock remains available through the KPI and inventory filter.
- Modules remain visible as compact roadmap cards with unfinished modules marked `Coming later`.
- Recent Activity uses DeliveryRecord data when available and ProductUnit fallback data for receiving until ReceivingRecord exists.
- Recent Activity rows and recent receiving/delivery panels are prepared for detail navigation through Operations placeholder routes.
- References use operational display formats such as `RCV-YYYY-0001` and `DLV-YYYY-0001`.
- Low Stock cards show product name, category, available quantity, and reorder threshold.
- Missing destination modules use simple BIM Nexus placeholder pages instead of dead links.
- Empty states use clean production wording.
- Pending modules are muted and marked `Coming later`.
- Command Center avoids accounting, invoice, payment, and support-ticket concepts.

## Next UI Focus

07 - Receiving Records.
