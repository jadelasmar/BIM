# Roadmap

This roadmap documents product direction, not implementation history.

## Completed / Active

- Command Center
- BIM Stock inventory list
- Product Details
- Add Product
- Receive Stock using `ReceivingRecord`
- Add Unit
- Create Delivery
- Delivery records API
- Receiving records backend API
- Receiving Records list frontend
- Receiving Record detail frontend
- Receiving record edit/cancel correction workflow
- Suppliers lookup API
- Django admin for stock and users
- Login and password setup
- Dark/light theme
- React/Vite/Tailwind frontend shell

## Current Product Focus

Build Delivery Records list/detail workflows.

The receiving records list, detail screen, Receive Stock form, and safe correction actions use operational receiving records under `/operations/receiving/`. Manual Add Unit remains a direct stock unit workflow under inventory.

## Near-Term Modules

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
