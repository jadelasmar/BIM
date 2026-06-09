# Current Structure

This file reflects the current implementation in the repository.

## Project

- Product/platform name: BIM Nexus
- Django project: `bim`
- Active Django app: `bim_stock`
- User-facing active module: BIM Stock
- Database: SQLite for current local development
- Timezone: `Asia/Beirut`
- Current frontend: React/Vite/Tailwind for Command Center; Django templates for login, admin, and existing BIM Stock pages
- Target frontend: expand React with Tailwind CSS across the main operational UI
- Node.js role: frontend build tooling only
- Runtime Django assets: `static/bim/assets/`
- React/Tailwind source: `frontend/src/`
- React build output served by Django: `static/frontend/`

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

Not implemented yet:
- DRF/API layer
- stock movement app/model
- receiving/delivery app
- companies/sites app
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
- `damaged`
- `returned`
- `inactive`

`Product` exposes active-only calculated stock count properties:
- `total_units`
- `available_units`
- `reserved_units`
- `sold_units`
- `damaged_units`
- `returned_units`

Status changes should be handled carefully because existing stock counts depend on these values.
Direct `ProductUnit` saves keep `sold_date` aligned with status:
- `sold` sets `sold_date` to the local date when it is blank.
- `available`, `reserved`, and `damaged` clear `sold_date`.
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
- list display with product identity, SKU, barcode, total/available/reserved/sold/damaged/returned quantities, type, category, brand, model, active state, created date
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

- Dashboard shows total active products, available units, sold units, and damaged units.
- Product list shows active products and available unit count.
- Product detail shows one active product and available unit count.
- Product detail shows available unit rows only to users with `bim_stock.view_productunit`.
- Stock unit list shows active stock units with status and pricing.

The React Command Center uses BIM Stock data for currently available KPIs and activity. Pending modules are shown as pending and are not backed by models yet.

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
