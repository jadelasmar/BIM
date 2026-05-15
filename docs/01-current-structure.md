# Current Structure

This file describes the current code structure and behavior that exists now.

## Django Project

Project name:
- bim

Main app:
- bim_stock

There is no React frontend app yet.

## Current Models

- Brand
- Type
- Category
- ProductModel
- Product
- ProductUnit
- Supplier

Not implemented yet:
- API layer
- stock movement model
- receiving/delivery app
- companies/sites app
- company assets app
- reusable attachments model
- knowledge base app
- reports app

## Current Pages

- `/admin/` Django admin
- `/accounts/login/` BIM Nexus login using Django auth
- `/accounts/logout/` secure POST logout using Django auth
- `/` protected BIM Nexus Command Center
- `/stock/` BIM Stock dashboard
- `/stock/products/` product list
- `/stock/products/<id>/` product detail with available units
- `/stock/units/` stock unit list

Core product models:
- Product
- ProductUnit
- Brand
- ProductModel
- Category

## Product Logic

Product represents the item definition.

Product fields:
- descript
- printed
- category
- model
- sku
- barcode, used for product-level barcode lookup
- image
- crdate
- isactive

Product type comes through Category.

Product brand comes through ProductModel.

SKU is auto-generated using:

CATEGORY-BRAND-MODEL

Example:
Printer + Zebra + GK888T = PRI-ZEB-GK888T

## ProductUnit Logic

ProductUnit represents one physical stock item.

Each ProductUnit belongs to one Product.

ProductUnit is used for:
- serial number
- stock status
- supplier
- cost
- selling price
- purchase date
- sold date
- notes
- active/inactive state

Current statuses:
- available
- reserved
- sold
- damaged
- returned

Planned status alignment for BIMPOS:
- keep current values until a model change session expands them safely
- future statuses should include delivered, transferred, and inactive if needed
- preserve existing data and SKU logic during any status migration

## Supplier Logic

Supplier represents the company or person products are bought from.

Supplier is connected to ProductUnit so each physical stock item can keep its own cost and purchase source.

## Pricing Logic

Supplier cost and client selling price are tracked on ProductUnit.

This keeps purchase cost and sale price tied to each physical stock item.

## Dashboard Logic

The BIM Stock dashboard shows:
- total active products
- active available units
- active sold units
- active damaged units

Low stock reporting is planned later after minimum stock quantity is added.

## Custom Stock Page Logic

Custom stock pages show active records first:
- product list shows active products and available unit count
- product detail shows product information and active available units
- stock unit list shows active ProductUnit records with status and pricing

Django admin remains the place for creating and editing stock records.

The current custom UI is Django templates, not React.

## Barcode Logic

Product barcode is stored on Product and can be searched from:
- Product admin
- ProductUnit admin through the related product
- custom product list
- custom stock unit list

ProductUnit does not have its own barcode yet. Unit-level barcode support is a future model change if serial number is not enough.

## Settings and Permissions

Current settings use:
- SQLite database
- Django auth/admin/session middleware
- Asia/Beirut timezone
- static files only through `STATIC_URL`

Current custom stock pages require login and Django `bim_stock` view permissions.

BIMPOS prepares these Django auth groups after migrations:
- Admin
- Stock Manager
- IT Support
- Viewer

The Command Center is the first post-login screen. It shows stock-backed KPIs, quick actions, recent stock activity, and module shortcuts. Future modules are shown as pending until their apps and APIs exist. Django admin remains available at `/admin/` for staff users.
