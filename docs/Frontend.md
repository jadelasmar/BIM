# Frontend

The frontend is a React/Vite/Tailwind app under `frontend/`.

## Source Structure

```text
frontend/src/
  App.jsx
  main.jsx
  styles.css
  assets/
    brand/
  components/
    common/
  constants/
  hooks/
  pages/
    auth/
  routes/
  utils/
```

## Entry Flow

- `main.jsx` reads JSON from `#bim-nexus-initial-data`.
- `App.jsx` is a lightweight wrapper.
- `routes/AppRouter.jsx` selects the page based on Django-provided data and `currentPath`.

## Routing

React does not use a client router package. Route selection is centralized in `AppRouter.jsx`.

Important rendered routes:

- `/` Command Center
- `/inventory/` Inventory list
- `/inventory/products/new/` Add Product
- `/inventory/products/<id>/` Product Details
- `/inventory/stock-units/new/` Add Unit
- `/operations/` Operations hub
- `/operations/receiving/` Receiving Records list
- `/operations/receiving/new/` Receive Stock
- `/operations/receiving/<id>/` Receiving Record detail
- `/operations/deliveries/` Delivery Records list
- `/operations/deliveries/new/` Create Delivery
- `/operations/deliveries/<id>/` Delivery Record detail
- `/operations/reservations/` Reservation Records list
- `/operations/reservations/new/` Create Reservation
- `/operations/reservations/<id>/` Reservation Record detail
- `/operations/issues/` Issue Records list
- `/operations/issues/new/` Create Issue
- `/operations/issues/<id>/` Issue Record detail
- `/operations/repairs/` Repair Records list
- `/operations/repairs/new/` Create Repair
- `/operations/repairs/<id>/` Repair Record detail
- `/settings/` Settings
- `/accounts/login/` Login
- `/accounts/setup/<uid>/<token>/` Password setup

## Pages

Current dedicated page folder:

- `pages/auth/AuthPages.jsx`

Most operational pages currently live in `routes/AppRouter.jsx`. Split pages gradually when feature work touches them.

Good future page split targets:

- `pages/dashboard/CommandCenter.jsx`
- `pages/inventory/InventoryPage.jsx`
- `pages/inventory/ProductDetailsPage.jsx`
- `pages/inventory/AddProductPage.jsx`
- `pages/inventory/StockEntryPage.jsx`
- `pages/inventory/CreateDeliveryPage.jsx`
- `pages/operations/ReceivingRecordsPage.jsx`

## Components

Reusable components:

- `components/common/Icon.jsx`
- `components/ui/Button.jsx`
- `components/ui/Card.jsx`
- `components/ui/Badge.jsx`
- `components/ui/Input.jsx`
- `components/ui/SearchBar.jsx`
- `components/ui/EmptyState.jsx`

Keep components small and extract only when reused or clearly feature-specific.

## Constants

- `constants/icons.js`: single Lucide icon source.
- `constants/statusStyles.js`: status badge classes and status icon metadata.
- `constants/uiRegistry.js`: frontend tones and workflow metadata.

Inventory stock status filters and badges use the office-ready ProductUnit set: available, reserved, issued, sold, repair, and inactive. Returned and damaged are not exposed as active stock statuses.

## Hooks

- `hooks/useTheme.js`: theme storage key, current theme, and theme application.

## Utilities

- `utils/formatters.js`: count, date, and currency display helpers.

## Assets

Editable brand assets:

- `frontend/src/assets/brand/logo-primary.svg`
- `frontend/src/assets/brand/logo-white.svg`

Generated hashed copies appear under `backend/static/frontend/assets/` after build.

## State Management

There is no global state library. Current state is local React state inside pages/components.

Add context only when state is genuinely shared across separate feature areas.

## API Access

API URLs are provided through Django `initial_data.api`. Current fetch calls are inline in `AppRouter.jsx`.

Create a service layer when fetch logic becomes shared across multiple pages.

Current Receiving Records integration:

- `/operations/receiving/new/` submits Receive Stock through `initial_data.api.receivingRecords`.
- Receive Stock creates one operational receiving record with item inputs, quantity-matched serial numbers, supplier/date/reference details, and reference-only costs.
- On success, Receive Stock redirects to `/operations/receiving/<id>/` when the API returns an id, otherwise back to the receiving records list.
- `/inventory/stock-units/new/` remains the manual Add Unit flow and still creates `ProductUnit` rows directly.
- `/operations/receiving/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/receiving-records/` through `initial_data.api.receivingRecords`.
- It shows operational receiving numbers, supplier/manual source, received date, reference number, item totals, and recorded status.
- Loading, empty, and error states reuse the existing table and empty-state patterns.
- Command Center receiving counts and recent receiving panels use real receiving records only. Manual Add Unit activity is direct inventory maintenance and is not shown as a receiving record.
- `/operations/receiving/<id>/` fetches one record through `initial_data.api.receivingRecordDetail`.
- The detail screen shows source, dates, reference, status, creator, notes, item lines, serial/unit links, and reference-only costs.
- The detail screen supports safe correction actions only:
  - Edit Details updates supplier, received date, reference number, notes, item cost, and item notes.
  - Cancel Record requires a cancellation reason and uses the receiving cancel API.
  - Product, quantity, and serial mistakes are handled by cancelling and recreating the record when linked units are still unused.
- If cancellation is blocked because a linked stock unit is already used, the detail screen shows the backend operational message.

Current Product Details movement integration:

- `/inventory/products/<id>/` fetches product movement history through `initial_data.api.productMovements`.
- The Product Details movement count uses real `StockMovement` rows instead of the previous placeholder count.
- The Movement History panel lists recent movement date, type, serial, from/to status, reference, user, and notes.
- Recent Activity on product detail is based on movement rows instead of inferring activity from current `ProductUnit.status`.
- If the user lacks stock movement view access, the page shows a permission-aware movement message and preserves product/unit detail behavior.

Current Reservation Records integration:

- `/operations/reservations/new/` submits Create Reservation through `initial_data.api.reservations`.
- The create screen loads active available stock units only and prevents selecting units that are already reserved, sold, inactive, or otherwise unavailable.
- On success, Create Reservation redirects to `/operations/reservations/<id>/` when the API returns an id, otherwise back to the reservation records list.
- `/operations/reservations/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/reservations/` through `initial_data.api.reservations`.
- It shows reservation number, reserved-for text, reason, expected release date, unit totals, and status.
- `/operations/reservations/<id>/` fetches one record through `initial_data.api.reservationDetail`.
- The detail screen shows reservation metadata, reserved item lines, and a Release Reservation action.
- Releasing a reservation requires a reason and returns linked untouched reserved units to available stock.
- Reserved units must be released before they can be delivered.

Current Issue Records integration:

- `/operations/issues/new/` submits Create Issue through `initial_data.api.issues`.
- The create screen loads active available stock units only and prevents selecting units that are already reserved, issued, sold, inactive, repair, or otherwise unavailable.
- On success, Create Issue redirects to `/operations/issues/<id>/` when the API returns an id, otherwise back to the issue records list.
- `/operations/issues/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/issues/` through `initial_data.api.issues`.
- It shows issue number, issued-to text, department/site, expected return date, unit totals, and status.
- `/operations/issues/<id>/` fetches one record through `initial_data.api.issueDetail`.
- The detail screen shows issue metadata, issued item lines, and a Return Issue action.
- Returning an issue requires a reason and returns linked untouched issued units to available stock.
- Issued units must be returned before they can be delivered.

Current Repair Records integration:

- `/operations/repairs/new/` submits Create Repair through `initial_data.api.repairs`.
- The create screen loads active available stock units only and prevents selecting units that are reserved, issued, sold, inactive, repair, or otherwise unavailable.
- On success, Create Repair redirects to `/operations/repairs/<id>/` when the API returns an id, otherwise back to the repair records list.
- `/operations/repairs/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/repairs/` through `initial_data.api.repairs`.
- It shows repair number, reason, location/technician, expected resolution date, unit totals, and status.
- `/operations/repairs/<id>/` fetches one record through `initial_data.api.repairDetail`.
- The detail screen shows repair metadata, repair item lines, and a Resolve Repair action.
- Resolving a repair requires resolution notes and moves linked untouched repair units either back to available or to inactive.
- Reserved units must be released/cancelled first, issued units must be returned first, and sold units must wait for a future client return workflow before repair.

Current Delivery Records integration:

- `/operations/deliveries/new/` submits Create Delivery through `initial_data.api.deliveries`.
- On success, Create Delivery redirects to `/operations/deliveries/<id>/` when the API returns an id, otherwise back to the delivery records list.
- `/operations/deliveries/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/deliveries/` through `initial_data.api.deliveries`.
- It shows delivery number, customer, receiver, delivery date, unit totals, and status.
- Loading, empty, and error states reuse the existing table and empty-state patterns.
- `/operations/deliveries/<id>/` fetches one record through `initial_data.api.deliveryDetail`.
- The detail screen shows customer, receiver, delivery date, status, creator, notes, total units, and delivered item lines with product, SKU, unit id, serial number, unit status, and notes.
- The detail screen supports safe correction actions only:
  - Edit Details updates customer, receiver, delivery date, notes, and item notes.
  - Cancel Record requires a cancellation reason and uses the delivery cancel API.
  - Wrong delivered unit, product, or serial mistakes are handled by cancelling and recreating the record when linked units are still untouched sold units.
- If cancellation is blocked because a linked stock unit is no longer an untouched sold unit, the detail screen shows the backend operational message.
