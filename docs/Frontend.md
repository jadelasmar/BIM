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
- `/operations/client-returns/` Client Return Records list
- `/operations/client-returns/new/` Create Client Return
- `/operations/client-returns/<id>/` Client Return Record detail
- `/suppliers/` Supplier list
- `/suppliers/new/` Create Supplier
- `/suppliers/<id>/` Supplier detail/edit
- `/clients/` Client list
- `/clients/new/` Create Client
- `/clients/<id>/` Client detail/edit
- `/settings/` Settings
- `/accounts/login/` Login
- `/accounts/setup/<uid>/<token>/` Password setup

## Pages

Current dedicated page folder:

- `pages/auth/AuthPages.jsx`

Most operational pages currently live in `routes/AppRouter.jsx`. Split pages gradually when feature work touches them.

The login page keeps Django form authentication authoritative while providing client-side required-field feedback for the email/username and password fields. Failed authentication restores only the trimmed email/username through Django initial data; passwords are never restored. The password visibility control uses state-aware `Eye` and `EyeOff` icons, and the account-access mail link uses the backend-configured `BIM_ADMIN_EMAIL` value.

The password setup page preserves submitted username, first name, and last name after backend validation errors. Both password fields always return empty after a failed submission. Required-field feedback is handled client-side before submission while Django remains authoritative for password strength, mismatch, token validity, and successful account creation.

The Command Center dashboard focuses on stock KPIs, system overview shortcuts, recent activity, recent deliveries, and recent receiving. Module navigation belongs in the sidebar rather than a duplicate dashboard modules section. Topbar Quick Add is limited to the common fast actions: Add Product, Add Unit, Receive Stock, and Create Delivery. Reservations, issues, repairs, client returns, receiving records, delivery records, and future movement history belong in the Operations hub. Supplier and Client cards show real active master-data counts and open the simple master-data modules.

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

Inventory stock status filters and badges use the office-ready ProductUnit set: available, reserved, issued, sold, repair, removed, and inactive. Returned and damaged are not exposed as active stock statuses.

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

Current Supplier and Client integration:

- `/suppliers/` and `/clients/` render simple master-data list screens.
- `/suppliers/new/`, `/clients/new/`, `/suppliers/<id>/`, and `/clients/<id>/` render create/edit screens for name, contact person, phone, email, notes, and active status.
- Receive Stock can select or create a Supplier inline.
- Create Delivery can select or create a Client inline. The API still sends `customer_name` for compatibility while linking the `client` master record.
- Create Client Return can select or create a Client inline.
- Supplier/Client create and edit buttons use backend-provided permission flags. Viewer can read these pages but does not see save/create controls.

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
- Reserved units must be released/cancelled first, issued units must be returned first, and sold units must go through Client Return before repair.

Current Client Return integration:

- `/operations/client-returns/new/` submits Create Client Return through `initial_data.api.clientReturns`.
- The create screen loads active sold stock units and lets the user choose either Return to available or Send to repair.
- The backend still requires selected units to be linked to active items on completed delivery records.
- On success, Create Client Return redirects to `/operations/client-returns/<id>/` when the API returns an id, otherwise back to the client return records list.
- `/operations/client-returns/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/client-returns/` through `initial_data.api.clientReturns`.
- It shows return number, original delivery number when available, client, received-from text, return date, unit totals, and resolution.
- `/operations/client-returns/<id>/` fetches one record through `initial_data.api.clientReturnDetail`.
- The detail screen shows return metadata and returned item lines with original delivery number, product, SKU, serial number, current unit status, and notes.
- Delivery detail includes a Create Client Return action that opens the create screen with the delivery id in the URL.
- Client Return is clearly labelled as not delivery cancellation and not a financial refund or credit.

Current Delivery Records integration:

- `/operations/deliveries/new/` submits Create Delivery through `initial_data.api.deliveries`.
- On success, Create Delivery redirects to `/operations/deliveries/<id>/` when the API returns an id, otherwise back to the delivery records list.
- `/operations/deliveries/` renders a real list screen from `AppRouter.jsx`.
- The screen fetches `/api/stock/deliveries/` through `initial_data.api.deliveries`.
- It shows delivery number, client, receiver, delivery date, unit totals, and status.
- Loading, empty, and error states reuse the existing table and empty-state patterns.
- `/operations/deliveries/<id>/` fetches one record through `initial_data.api.deliveryDetail`.
- The detail screen shows client, receiver, delivery date, status, creator, notes, total units, and delivered item lines with product, SKU, unit id, serial number, unit status, and notes.
- The detail screen supports safe correction actions only:
  - Edit Details updates client, receiver, delivery date, notes, and item notes.
  - Cancel Record requires a cancellation reason and uses the delivery cancel API.
  - Wrong delivered unit, product, or serial mistakes are handled by cancelling and recreating the record when linked units are still untouched sold units.
- If cancellation is blocked because a linked stock unit is no longer an untouched sold unit, the detail screen shows the backend operational message.

## Generic (no-serial) units in the UI

- Receive Stock sends only typed/scanned serials plus `auto_serial_count`; Add Unit omits `serial_number` when none was typed. The backend makes and flags the serials. A blank serial box means "generic unit".
- The unit pickers (Create Delivery, Reservation, Temporary Assignment/Issue, Repair, Removal, Client Return) share `buildUnitPickerRows`, `UnitPickerResults`, `GenericUnitRow` and `groupSelectedUnits` in `AppRouter.jsx`. Per product (and status), generic units are one row: "No serial - N available" with a quantity input and Add. The quantity takes the oldest units first (`oldestGenericUnits`: receiving/entry date, undated last, then id). Real-serial units stay one row each, and mixing both in one record is allowed. A generic unit is found by product text, not by its made-up serial; scanning an exact serial (generated or real) still selects that unit.
- Selected lists show generic units of one product as one row with a count and one remove button. Create Delivery's reference sale price is one input per merged row, applied to each unit in it.
- Client Return takes generic units from `returnable-generic-groups/`: one row per product and client ("N returnable"), oldest delivery first; once a unit is picked only that client's rows are offered.
- Record detail item tables (Receiving, Delivery, Reservation, Issue, Repair, Removal, Client Return) merge identical generic lines through `groupGenericItems` into "No serial / N units"; real serials list individually. The Receiving and Delivery edit panels edit a merged line for every item in it.
- Inventory Stock Units view still lists every unit with its serial and adds a Serial Type column (Generated / Real); its CSV gains `Serial Type` after `Serial Number`. The Product Details unit register tags generated serials.
- There is no printed note/PDF view in the app; if one is added it must reuse `groupGenericItems`.

## Inventory CSV Export

The Inventory page Export button (`exportCurrentView` in `AppRouter.jsx`) downloads the current view through `downloadCsv` (UTF-8 BOM so Excel opens it directly). It is the only product-level stock export in the app.

Products view (`inventory-<date>.csv`): one row per ungrouped product and one row per product group, in the on-screen sort order. A group's row uses the group name and its merged stock numbers; its member products are not listed, and its Category/Brand/Model are empty. Columns, in order:

`Product, Category, Brand, Model, Total In Stock, Available, Reserved, Issued (temporary), In Repair, Reserved For, Assigned To, Repair At, Status`

- SKU, Barcode, Sold, Removed, Low Stock Alert and Group are not exported here (SKU is in the Stock Units export).
- Total In Stock is available + reserved + issued + repair; sold and removed units never count toward it. Counts come from the inventory row (`total_units`, `available_units`, `reserved_units`, `issued_units`, `repair_units`; for a group, its merged `group_stock` numbers).
- Reserved For / Assigned To / Repair At list each party with its unit count, e.g. `Acme Ltd (2); Beta Co (1)`, empty when none. They are derived from the same per-unit "where" text as the Stock Units view ("Reserved for X", "With X", "At <vendor>"), fetched on export from the existing `product-units?with_location=1` endpoint (only when a listed product has reserved, issued or repair units). A repair with no supplier shows as `No supplier`. If that fetch fails, a toast is shown and nothing is downloaded.
- "Assigned To" is the UI's own term for the Issue workflow's party (Temporary Assignments).

Stock Units view (`stock-units-<date>.csv`): `Serial Number, Serial Type, Product, SKU, Status, Where, Supplier, Cost, Purchase Date, Notes, Group` (`Serial Type` is `Generated` or `Real`).

## Role-Aware Actions

- Admin / IT lead accounts can use Django Admin when `is_staff` or superuser access is granted.
- IT Support can use normal stock workflow actions exposed by its Inventory add/change/view permissions.
- Viewer can open dashboard, inventory, master-data, records, and movement-history screens, but frontend create/edit/cancel/return/resolve controls are hidden where permission flags are available.
- Backend APIs still enforce permissions directly; frontend hiding is usability, not security.
