# Current Structure

This file reflects the current implementation in the repository.

## Project

- Product/platform name: BIM Nexus
- Django project: `bim`
- Active Django app: `bim_stock`
- User-facing active module: BIM Stock
- Database: SQLite for current local development
- Timezone: `Asia/Beirut`
- Current frontend: React/Vite/Tailwind for Command Center and Inventory; Django templates for login, admin, and existing BIM Stock pages
- Target frontend: expand React with Tailwind CSS across the main operational UI
- Node.js role: frontend build tooling only
- Runtime Django assets: `static/bim/assets/`
- React/Tailwind source: `frontend/src/`
- React build output served by Django: `static/frontend/`
- Shared theme/font assets: `static/bim/theme.css`, `static/bim/theme-init.js`, `static/bim/theme.js`

## Frontend Asset Structure

Current runtime static asset buckets:

```text
static/bim/assets/
|-- brand/
|-- images/
|-- icons/
|-- illustrations/
|-- screenshots/
`-- backgrounds/
```

React/Tailwind asset buckets:

```text
frontend/src/assets/
|-- brand/
|-- images/
|-- icons/
|-- illustrations/
`-- backgrounds/
```

Branding assets are centralized in both places for now:
- `static/bim/assets/brand/` keeps the current Django templates working.
- `frontend/src/assets/brand/` is the source path prepared for the future React/Vite app.

## Installed Business Apps

- `bim_stock`

`bim_stock` is the implementation app for the BIM Stock module inside BIM Nexus.
Future business areas should follow this pattern: one focused Django app per
major workflow, exposed as a module in the Command Center.

## Installed Platform Apps

- `bim_accounts`

`bim_accounts` owns BIM Nexus account helpers on top of Django auth:
- username-or-email login
- unique email validation in Django admin
- required email on Django admin user edits
- email-only admin user creation
- admin-generated manual account setup links
- first name, last name, username, and password setup through a secure token URL

Implemented API layer:
- DRF is installed and uses Django session authentication.
- Inventory API endpoints are exposed under `/api/stock/` for React screens.

Not implemented yet:
- stock movement app/model
- receiving records app/model
- delivery records app/model
- companies app
- forms/documents app
- company assets app
- reusable attachments
- knowledge base app
- reports app

## URLs

- `/admin/` Django admin
- `/accounts/login/` BIM Nexus login using Django auth
- `/accounts/logout/` Django auth logout, POST-only
- `/accounts/setup/<uid>/<token>/` secure username/password setup/reset link
- `/` protected BIM Nexus Command Center, rendered by React/Tailwind through Django auth
- `/settings/` protected React/Tailwind Settings page with the shared dark/light appearance toggle
- `/inventory/` protected React/Tailwind Inventory page
- `/inventory/products/new/` protected React/Tailwind Add Product page
- `/inventory/products/<id>/` protected React/Tailwind Product Details page
- `/inventory/receiving/new/` protected React/Tailwind Receive Stock page
- `/api/stock/summary/` inventory count summary API
- `/api/stock/products/` product list/create API
- `/api/stock/products/<id>/` product detail/update API
- `/api/stock/product-units/` stock unit list/create API
- `/api/stock/product-units/<id>/` stock unit detail/update API
- `/api/stock/types/` product type lookup API
- `/api/stock/categories/` category lookup API
- `/api/stock/brands/` brand lookup API
- `/api/stock/models/` product model lookup API
- `/api/stock/suppliers/` supplier lookup API
- `/stock/` BIM Stock dashboard
- `/stock/products/` product list
- `/stock/products/<id>/` product detail
- `/stock/units/` stock unit list

## Models

Current `bim_stock` models:
- `Type`
- `Category`
- `Brand`
- `ProductModel`
- `Product`
- `Supplier`
- `ProductUnit`

## Product Logic

`Product` is the reusable product definition, not one physical stock item.

Fields:
- `descript`
- `printed`
- `category`
- `model`
- `sku`
- `barcode`
- `image`
- `minimum_stock_level`
- `reorder_stock_level`
- `crdate`
- `isactive`

Naming conventions currently in code:
- `descript` stores the internal description
- `printed` stores the display/printed name
- `crdate` stores created date/time
- `isactive` is the active flag

SKU is generated automatically from category, brand, and model:

```text
CATEGORY-BRAND-MODEL
```

Example:

```text
Printer + Zebra + GK888T = PRI-ZEB-GK888T
```

Do not change SKU logic unless explicitly requested.

## ProductUnit Logic

`ProductUnit` is one physical stock item.

Fields:
- `product`
- `serial_number`
- `status`
- `supplier`
- `cost`
- `selling_price`
- `purchase_date`
- `sold_date`
- `notes`
- `crdate`
- `isactive`

Current statuses:
- `available`
- `reserved`
- `sold`
- `returned`
- `inactive`

`Product` exposes active-only calculated stock count properties:
- `total_units`
- `available_units`
- `reserved_units`
- `sold_units`
- `returned_units`
- `is_low_stock`
- `is_critical_stock`
- `stock_alert_tone`

Status changes should be handled carefully because existing stock counts depend on these values.
Direct `ProductUnit` saves keep `sold_date` aligned with status:
- `sold` sets `sold_date` to the local date when it is blank.
- `available`, `reserved`, and `inactive` clear `sold_date`.
- `returned` can keep the previous sold date for audit context.

## Admin Structure

Registered directly:
- `Type`
- `Category`
- `Brand`
- `ProductModel`

Custom admin:
- `ProductAdmin`
- `SupplierAdmin`
- `ProductUnitAdmin`

`ProductAdmin` includes:
- list display with product identity, SKU, barcode, total/available/reserved/sold/returned quantities, minimum/reorder stock levels, stock alert, type, category, brand, model, active state, created date
- search by description, printed name, SKU, barcode
- filters by category, brand, active state
- readonly `sku` and `crdate`
- stock quantity annotations for admin list performance

`SupplierAdmin` includes:
- search by name
- ordering by name

`ProductUnitAdmin` includes:
- purchase defaults for new units
- list display for product, serial number, status, supplier, cost, selling price, dates, active state
- filters by status, product category, product brand, supplier, active state, purchase date, sold date
- search by serial number and related product identifiers
- readonly `crdate`
- autocomplete for product and supplier
- action to mark selected units as sold

## Current Custom Pages

The custom stock pages show active records.

- Dashboard shows total active products, available units, sold units, and low-stock products.
- Product list shows active products and available unit count.
- Product detail shows one active product and available unit count.
- Product detail shows available unit rows only to users with `bim_stock.view_productunit`.
- Stock unit list shows active stock units with status and pricing.

The React Command Center uses BIM Stock data for currently available KPIs and activity. Pending modules are shown as pending and are not backed by models yet.
The React Inventory page uses the stock API for the product table, filters, KPI summary, and product detail panel.
Clicking a product in the React Inventory table opens the React Product Details page.
The React Add Product page uses the Product API to create product definitions. It can submit an existing `model` id or a `brand` plus `model_name_input`; the API creates the missing `ProductModel` when needed and preserves auto-generated SKU logic.
The React Product Details page uses the Product API plus filtered ProductUnit API data for stock counts, supplier-derived information, stock availability, and recent activity.
The React Receive Stock page creates available `ProductUnit` records through the ProductUnit API. It is a stock-unit intake workflow, not a full receiving-note model yet.

## Shared Theme

BIM Nexus uses the shared `bim-nexus-theme` localStorage key for dark/light mode.
The Settings page at `/settings/` is the main place to change theme.
React pages, login/setup pages, and custom BIM Stock Django templates load the shared theme/font assets from `static/bim/`.
The shared font stack is defined by `--bim-font-family` and should be used by future pages.

## Future Operational Records

BIM Nexus should not become purchasing, invoicing, accounting, or payment software. Official invoices stay in accounting software. BIM Nexus should store only operational references needed to understand stock history.

Future receiving records:
- internal stock-entry records
- numbered like `RCV-YYYY-0001`
- can store supplier, receiving date, optional invoice/reference text, notes, and received items
- completing a receiving record should increase stock by creating/updating `ProductUnit` records
- completing a receiving record should generate stock movement history

Future delivery records:
- internal stock-exit or dispatch records
- numbered like `DLV-YYYY-0001`
- can store company/customer, receiver, deliverer, signature details, notes, and delivered items
- completing a delivery record should reduce/update stock by changing `ProductUnit` status
- completing a delivery record should generate stock movement history

Future stock movements:
- mainly audit/history records generated by receiving, delivery, return, or adjustment actions
- not the primary workflow for normal receiving or delivery
- may still support direct adjustment workflows where needed

Future forms/documents:
- separate non-stock paperwork module
- examples include installation reports, maintenance forms, signed scans, PDFs, photos, and general documents
- may link to supplier, company, asset, product, or stock history
- should not affect stock unless explicitly connected to an inventory workflow

Operational numbering should use readable prefixes such as `RCV-YYYY-0001`, `DLV-YYYY-0001`, `DOC-YYYY-0001`, and `AST-YYYY-0001` where needed.

## Permissions

Current custom stock pages require login and Django `bim_stock` view permissions.

Internal users are created by staff/admin users, not through public sign-up.
New users are created with a unique email first, then enter first name, last name, username, and password from the setup link.
If username is left blank during setup, it defaults to the email name before `@`.
Users can log in with either username or email after setup.
User emails must be unique and required because email login maps one address to one account.
Initial names, usernames, and passwords are created through admin-generated manual setup links.
New users start in the `Viewer` group unless a staff user changes their group.

Prepared groups:
- Administrator: all BIM Stock permissions
- Operations Manager: view, add, and change BIM Stock permissions
- IT Support: view and change BIM Stock permissions, without adding new stock
- Viewer: view-only BIM Stock permissions

Django admin remains available for staff users.
