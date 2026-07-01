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
- Receiving records backend API
- Suppliers lookup API
- Django admin for stock and users
- Login and password setup
- Dark/light theme
- React/Vite/Tailwind frontend shell

## Current Product Focus

Build full Receiving Records frontend workflows.

The backend now has operational receiving records. The current receiving UI still creates `ProductUnit` records directly and should move to the receiving record API when the list/detail workflow is built.

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
