# Development Progress

## Current Phase

Command Center is complete for Phase 1.

## Backend

- Django remains the backend and source of truth.
- Product and ProductUnit power BIM Stock counts.
- DeliveryRecord powers delivery activity and delivery-record counts where available.
- Receiving activity still uses ProductUnit fallback data until ReceivingRecord is implemented.
- `/api/command-center/` returns the protected dashboard payload used for 60-second Command Center auto-refresh.
- Dashboard references use operational formats only: `RCV-YYYY-0001`, `DLV-YYYY-0001`, `PRD-YYYY-0001`, and `ADJ-YYYY-0001`.
- No accounting, invoicing, payment, or support-ticket logic is part of BIM Nexus.

## Frontend

- React/Vite/Tailwind powers Command Center, BIM Stock, Operations, Product Detail, Add Product, Receive Stock, and Create Delivery screens.
- Shared UI naming, icon, tone, and status mappings are centralized in:
  - `bim/ui_registry.py`
  - `frontend/src/uiRegistry.js`
- Related workflow actions and summaries should use the same registry icon and tone. Example: Delivery Records and Create Delivery both use `delivery` with the indigo tone.

## Verification Baseline

- Django check should pass.
- Django migrations check should show no pending model migrations unless a focused model change was made.
- Django tests should pass.
- Frontend build should pass from `frontend/`.

## Next Development Focus

06 - Product Details.
