# Roadmap

This roadmap documents product direction, not implementation history.

## Completed / Active

- Command Center
- BIM Stock inventory list
- Product Details
- Add Product
- Receive Stock using `ProductUnit`
- Add Unit
- Create Delivery
- Delivery records API
- Suppliers lookup API
- Django admin for stock and users
- Login and password setup
- Dark/light theme
- React/Vite/Tailwind frontend shell

## Current Product Focus

Build full Receiving Records.

The current receiving UI creates `ProductUnit` records directly. A durable receiving workflow should introduce receiving records when the process needs record numbers, detail pages, auditability, and reporting.

## Near-Term Modules

- Receiving Records list/detail
- Delivery Records list/detail
- Supplier page
- Product edit workflow
- Better stock history views

## Future Modules

- Clients
- Assets
- Knowledge Base
- Reports
- Forms/Documents
- Notifications
- Audit logs
- Search
- Users/Roles operational UI

## Explicit Non-Goals

BIM Nexus is not:

- accounting software
- invoicing software
- payment software
- financial posting software
- public signup software
- ticketing or Tasklogger replacement software

Accounting software owns official invoices, payments, and financial posting.

