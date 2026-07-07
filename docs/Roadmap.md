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
- Delivery Records list frontend
- Delivery Record detail frontend
- Delivery record edit/cancel correction workflow
- Receiving records backend API
- Receiving Records list frontend
- Receiving Record detail frontend
- Receiving record edit/cancel correction workflow
- StockMovement operational ledger foundation
- Reservation records workflow
- Issue and return-from-issue workflow
- Repair workflow
- Client return workflow using sold-to-available and sold-to-repair transitions
- Office-ready ProductUnit status vocabulary
- First office testing/deployment checklist
- Suppliers lookup API
- Django admin for stock and users
- Login and password setup
- Dark/light theme
- React/Vite/Tailwind frontend shell

## Current Product Focus

Prepare and run first internal office testing before moving to reports or secondary modules.

Receiving and delivery records now have operational create/list/detail workflows under `/operations/...`. Manual Add Unit remains a direct stock unit workflow under inventory.

StockMovement now records receiving, receiving cancellation, delivery, delivery cancellation, reservation, reservation release, issue, issue return, repair creation, repair resolution, client return creation, manual Add Unit, and direct product-unit status update movements going forward. The ProductUnit status set is now available, reserved, issued, sold, repair, and inactive. Client Return v1 moves sold units to available or repair without adding a permanent returned status.

## Near-Term Modules

- Supplier page
- Product edit workflow
- Better stock history views
- Broader office stock polish around search, audit views, and operational usability

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
