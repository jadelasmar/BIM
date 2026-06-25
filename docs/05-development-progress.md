# Development Progress

## Current Phase

Command Center is complete for Phase 1.

## Backend

- Django remains the backend and source of truth.
- Product and ProductUnit power BIM Stock counts.
- DeliveryRecord powers delivery activity and delivery-record counts where available.
- Receiving activity still uses ProductUnit fallback data until ReceivingRecord is implemented.
- `/api/command-center/` returns the protected dashboard payload used for 60-second Command Center auto-refresh.
- Command Center KPI and System Overview payloads include `href` destinations so cards act as navigation shortcuts.
- Missing destination modules use protected React placeholder routes until their real workflows are implemented.
- Command Center layout is compact for Phase 1: Search, KPI cards, System Overview, compact Modules roadmap, Recent Activity, Recent Deliveries, and Recent Receiving.
- Quick Add remains in the topbar; the old large Quick Actions panel is no longer rendered.
- Dashboard references use operational formats only: `RCV-YYYY-0001`, `DLV-YYYY-0001`, `PRD-YYYY-0001`, and `ADJ-YYYY-0001`.
- No accounting, invoicing, payment, or support-ticket logic is part of BIM Nexus.

## Frontend

- React/Vite/Tailwind powers Command Center, BIM Stock, Operations, Product Detail, Add Product, Create Delivery, Receive Stock, and Add Unit screens.
- Shared UI naming, icon, tone, and status mappings are centralized in:
  - `bim/ui_registry.py`
  - `frontend/src/uiRegistry.js`
- Related workflow actions and summaries should use the same registry icon and tone. Example: Delivery Records and Create Delivery both use `delivery` with the indigo tone.
- Product Details renders product metrics, supplier/stock information, active stock units, and permission-aware workflow actions from existing BIM Stock APIs.
- BIM Stock list row clicks update the inline Product Detail panel; only Full
  View navigates to `/inventory/products/<id>/`.
- BIM Stock list KPI cards reuse the same shared React KPI card component as
  Command Center.
- Add Product can create Category and Brand lookup records through the stock API without requiring Django admin.
- Product setup uses one `reorder_stock_level` threshold for low-stock alerts;
  the separate printed name and minimum-stock fields were removed.
- Add Product supports product image click/drop selection and saves images through multipart product API requests.
- Legacy Django stock template routes under `/stock/` were removed; React
  `/inventory/` and the stock APIs are the active stock surfaces.
- Use `Clients` terminology in Command Center navigation. Do not reintroduce Sites for this phase.

## Verification Baseline

- Django check should pass.
- Django migrations check should show no pending model migrations unless a focused model change was made.
- Django tests should pass.
- Frontend build should pass from `frontend/`.

## Next Development Focus

07 - Receiving Records.
