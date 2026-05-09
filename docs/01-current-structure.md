# Current Structure

## Django Project

Project name:
- bim

Main app:
- bim_stock

## Current Models

- Brand
- Type
- Category
- ProductModel
- Product
- ProductUnit
- Supplier

## Current Pages

- `/admin/` Django admin
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
- barcode
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
