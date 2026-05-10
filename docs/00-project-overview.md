# BIM Project Overview

This file explains the project goal and the business modules planned for BIM.

BIM is a Django-based internal company platform.

The project should stay modular. Each main business area should be built as its own Django app, but the apps can still be connected and share data.

Example:
- BIM Stock owns products and inventory
- Receiving / Delivery can select products from BIM Stock
- if a product does not exist yet, it should be created in BIM Stock first

## Current App

- BIM Stock

BIM Stock is the only implemented business app right now.

BIM Stock is used to manage inventory, products, quantities, suppliers, cost, selling status, and client pricing later.

Main goals:
- check stock
- buy products from suppliers
- sell products to clients
- track product quantity
- track supplier cost
- track client price later
- track serial numbers where needed
- keep stock status clear
- track minimum quantity needed in stock
- show what needs restocking

## Usage Goal

BIM is being built for internal company use first.

If BIM Stock works well, it may later be used by other users or companies.

Build choices should support that later without overbuilding now:
- keep data clean
- keep workflows simple
- use clear names
- avoid hardcoding one company only
- add user permissions before real multi-user use
- keep future reporting and exports in mind

## Planned App

- Receiving / Delivery

Receiving / Delivery will create simple printable documents from templates.

Receiving / Delivery should use products already created in BIM Stock.

The printable form should allow filling:
- products
- company
- receiver
- deliverer
- date
- notes

## Future Possible Apps

- BIM Support
- BIM Tasks
- BIM Reports
- BIM Integrations
