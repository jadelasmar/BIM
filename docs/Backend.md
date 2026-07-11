# Backend

The backend is a Django project under `backend/`.

## Project Package

`backend/bim/` is configuration-only:

- `settings.py`
- `urls.py`
- `asgi.py`
- `wsgi.py`
- `__init__.py`

Do not put business logic in this package.

## Apps

### `apps.core`

Owns shared backend shell behavior:

- protected React app launcher
- Command Center initial data
- `/api/command-center/`
- backend UI token config in `ui_config.py`
- Vite manifest template tag

Core may compose stock selector output, but stock query logic belongs in `apps.stock`.

### `apps.accounts`

Owns account behavior on top of Django auth:

- email-or-username login
- password setup page data
- secure setup links
- custom admin user creation
- unique email enforcement
- default Viewer group assignment

There is no public signup.

### `apps.stock`

Owns BIM Stock:

- product hierarchy
- product definitions
- physical stock units
- suppliers
- clients
- receiving records and receiving items
- delivery records and delivery items
- reservation records and reservation items
- issue records and issue items
- repair records and repair items
- stock movements
- stock selectors
- stock API views and serializers
- admin configuration
- role preparation
- migrations and tests

The package path is `apps.stock`, but the Django app label remains `bim_stock` for migration and permission compatibility.

## Authentication And Permissions

- Django sessions authenticate users.
- DRF uses `SessionAuthentication`.
- Default DRF permission is `IsAuthenticated`.
- API views perform explicit permission checks using constants in `backend/apps/stock/constants.py`.
- Stock roles are prepared in `backend/apps/stock/roles.py`.
- New users are assigned to the Viewer group by account signals.
- Admin / IT lead users should remain superuser or staff-level accounts when they need Django Admin, user, group, permission, or system settings access.
- IT Support is the daily stock operations role. It receives BIM Stock view/add/change permissions except delete permissions, so it can create and correct stock records, products, units, suppliers, and clients without managing Django users/groups/settings.
- Viewer is read-only. It receives BIM Stock view permissions only and cannot create, edit, cancel, return, resolve, or insert records through the APIs.
- Initial app data exposes stock action permission flags so the frontend can hide write actions for Viewer while backend API checks remain authoritative.

## Views

Core views:

- `module_launcher`: renders the React shell template.
- `command_center_data`: returns Command Center JSON.

Account views:

- `login_view`: validates login and renders React login page data, including `BIM_ADMIN_EMAIL` and only the trimmed submitted identifier after a failed login. Password values are never returned in page data.
- `password_setup_confirm`: validates setup token and renders React setup page data.

Stock API views:

- product list/create/detail/update
- product unit list/create/detail/update
- receiving record list/create/detail/update
- receiving record cancel
- delivery list/create/detail/update
- delivery cancel
- reservation list/create/detail
- reservation release/cancel
- issue list/create/detail
- issue return
- repair list/create/detail
- repair resolve
- supplier list/create/detail/update
- client list/create/detail/update
- client return list/create/detail
- product movement history
- inventory summary
- lookup endpoints for categories, brands, models, suppliers, clients

Delivery record list search currently supports delivery number, linked client name, compatibility client text, receiver name, product-unit serial number, product description, and product SKU. The API field `customer_name` remains for compatibility, while new office records can also link to `client`. Delivery list/detail access uses the delivery record view permission. Creating a delivery requires both the delivery record add permission and product-unit change permission because selected stock units are marked sold.

Create Delivery only accepts active available product units. Reserved units must be released before they can be delivered.

Delivery correction is intentionally limited:

- Safe header updates may change client name, receiver name, delivery date, and notes.
- Safe line updates may change delivery item notes only.
- Product-unit links, products, delivered units, serial numbers, and delivered quantity are not editable through the delivery correction API.
- Changing the delivery date is blocked unless every linked stock unit is still active, sold, and linked to this delivery item.
- Cancellation requires the delivery record change permission and product-unit change permission.
- Cancellation is blocked when any linked product unit is no longer an untouched sold unit for that delivery.
- Successful cancellation marks the delivery record cancelled, stores cancellation audit fields, marks delivery items inactive, and returns linked product units to available stock.

Receiving record list search currently supports receiving number, supplier name, reference number, product description/SKU, receiving item serial number, and linked product-unit serial number. Future reporting should reuse the `ReceivingRecord` header fields and `ReceivingItem` product/unit relationships instead of querying generated frontend data.

Receiving correction is intentionally limited:

- Safe header updates may change supplier, reference number, received date, and notes.
- Safe line updates may change receiving item cost and notes only.
- Product, quantity, product-unit link, and serial number are not editable through the receiving correction API.
- Cancellation requires the receiving record change permission.
- Cancellation also requires product-unit change permission when linked stock units are affected.
- Cancellation is blocked when any linked product unit is not active and available, or has already been delivered.
- Successful cancellation marks the receiving record cancelled/inactive, marks its receiving items inactive, and marks linked available product units inactive.

## Selectors

Stock read/query helpers live in `backend/apps/stock/selectors.py`.

Use selectors for reusable read logic that feeds dashboards, summaries, and app-shell data.

Dashboard receiving counts and recent receiving panels are based on real active `ReceivingRecord` rows. ProductUnit-only rows from manual Add Unit are inventory maintenance records, not receiving records.

Recent delivery panels and delivery activity are based on real active `DeliveryRecord` rows. Sold `ProductUnit` rows that are not linked to a delivery item are not shown as delivery records and must not generate fake delivery detail links.

Product movement history is based on real `StockMovement` rows. Product detail can read recent movement rows through `/api/stock/products/<id>/movements/`, which requires the stock movement view permission.

Product unit statuses for office deployment are `available`, `reserved`, `issued`, `sold`, `repair`, and `inactive`. `returned` and `damaged` are not active status values. Client Return moves sold units back to available or repair through its own operational record.

Reservation record list search supports reservation number, reserved-for text, reason, product-unit serial number, product description, and product SKU. Reservation list/detail access uses the reservation record view permission. Creating a reservation requires both the reservation record add permission and product-unit change permission because selected stock units are marked reserved. Releasing or cancelling a reservation requires both reservation record change permission and product-unit change permission because linked units return to available stock.

Issue record list search supports issue number, issued-to text, department, branch/site, reason, product-unit serial number, product description, and product SKU. Issue list/detail access uses the issue record view permission. Creating an issue requires both the issue record add permission and product-unit change permission because selected stock units are marked issued. Returning an issue requires both issue record change permission and product-unit change permission because linked units return to available stock.

Create Issue only accepts active available product units. Issued units cannot be delivered directly by Create Delivery; they must be returned to available first.

Repair record list search supports repair number, repair reason, reported-by text, repair location, technician, product-unit serial number, product description, and product SKU. Repair list/detail access uses the repair record view permission. Creating a repair requires both repair record add permission and product-unit change permission because selected stock units are marked repair. Resolving a repair requires both repair record change permission and product-unit change permission because linked units return to available or are made inactive.

Create Repair only accepts active available product units. Reserved units must be released/cancelled first, issued units must be returned first, and sold units must go through Client Return before they can enter repair.

Client return record list search supports return number, original delivery number, linked client name, compatibility client text, received-from text, reason, product-unit serial number, product description, and product SKU. The API field `customer_name` remains for compatibility, while new office records can also link to `client`. Client return list/detail access uses the client return record view permission. Creating a client return requires both client return record add permission and product-unit change permission because selected sold units are moved back to available or repair.

Create Client Return only accepts active sold product units linked to active items on completed delivery records. It blocks duplicate returns through active return-item checks and blocked status checks. Delivery cancellation remains a separate correction workflow; client return is a real operational return event and does not change the original delivery record status.

## Services

Stock write workflows that span multiple models live in `backend/apps/stock/services.py`.

Current services:

- `create_stock_movement`: centralized helper for operational stock movement rows.
- `create_receiving_record`: creates operational receiving records and items, and creates/links `ProductUnit` rows when serial numbers are supplied.
- `update_receiving_record_header`: updates safe receiving header fields and line cost/notes, synchronizing available linked stock-unit purchase metadata.
- `cancel_receiving_record`: cancels a receiving record only while linked stock units are still unused and available.
- `create_delivery_record`: creates operational delivery records and items, marks selected product units sold, and records delivery movements.
- `update_delivery_record_header`: updates safe delivery header fields and delivery item notes, synchronizing sold dates only for untouched sold units.
- `cancel_delivery_record`: cancels a delivery record only while linked stock units are still untouched sold units for that delivery.
- `create_reservation_record`: creates operational reservation records and items, marks selected available product units reserved, and records reservation movements.
- `release_reservation_record`: releases or cancels a reservation only while linked stock units are still untouched reserved units for that reservation.
- `create_issue_record`: creates operational issue records and items, marks selected available product units issued, and records issue movements.
- `return_issue_record`: returns an issue only while linked stock units are still untouched issued units for that issue.
- `create_repair_record`: creates operational repair records and items, marks selected available product units repair, and records repair movements.
- `resolve_repair_record`: resolves a repair only while linked stock units are still untouched repair units for that repair, returning units to available or making them inactive.
- `create_client_return_record`: creates operational client return records and items, validates selected units are active sold units linked to completed delivery items, moves them to available or repair, clears sold date, and records client-return movements.

Receiving creation, receiving cancellation, delivery creation, delivery cancellation, reservation creation, reservation release/cancel, issue creation, issue return, repair creation, repair resolution, client return creation, manual Add Unit, and direct product-unit status updates now write `StockMovement` rows going forward. Clean deployments do not need legacy backfill.

Keep views thin. Broader stock adjustment workflows should write movements through services instead of direct ad hoc model updates.

## Admin

Django admin remains a supported operational surface for non-technical staff. Admin configuration should stay readable, searchable, and permission-aware.
