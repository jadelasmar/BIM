# Current Structure

This file reflects the current implementation in the repository.

## Project

- Django project: `bim`
- Active Django app: `bim_stock`
- Database: SQLite for current local development
- Timezone: `Asia/Beirut`
- Frontend: Django templates only; no React/Vite app exists yet

## Installed Business Apps

- `bim_stock`

Not implemented yet:
- API layer
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
- `/` protected BIM Nexus Command Center
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

Status changes should be handled carefully because existing stock counts depend on these values.

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
- list display with product identity, SKU, barcode, available quantity, type, category, brand, model, active state, created date
- search by description, printed name, SKU, barcode
- filters by category, brand, active state
- readonly `sku` and `crdate`
- available quantity annotation

`SupplierAdmin` includes:
- search by name
- ordering by name

`ProductUnitAdmin` includes:
- purchase defaults for new units
- list display for product, serial number, status, supplier, cost, selling price, dates, active state
- filters by status, supplier, active state, purchase date, sold date
- search by serial number and related product identifiers
- readonly `crdate`
- autocomplete for product and supplier
- action to mark selected units as sold

## Current Custom Pages

The custom stock pages show active records.

- Dashboard shows total active products, available units, sold units, and damaged units.
- Product list shows active products and available unit count.
- Product detail shows one active product and active available units.
- Stock unit list shows active stock units with status and pricing.

The Command Center uses BIM Stock data for currently available KPIs and activity. Pending modules are shown as pending and are not backed by models yet.

## Permissions

Current custom stock pages require login and Django `bim_stock` view permissions.

Prepared groups:
- Admin
- Stock Manager
- IT Support
- Viewer

Django admin remains available for staff users.
