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
