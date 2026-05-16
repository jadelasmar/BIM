# BIM Stock Session Plan

This file tracks focused implementation sessions. Use one session per task.

## Completed BIM Stock Work

1. Product admin cleanup
2. ProductUnit admin cleanup
3. Stock count display
4. Product pricing fields
5. Purchase workflow defaults
6. Selling workflow through admin action
7. Stock dashboard
8. Custom stock pages
9. Product barcode support
10. Stock UI polish
11. Login, roles, protected pages, and Command Center

## Before Wider Use

Before BIM Stock is used by more people:
- harden user roles and permissions
- add audit history for stock changes
- confirm backup plan
- review security settings
- test common workflows with real data
- add exports for stock reports

## Next Order

1. Login UI from Figma
2. Stock & Inventory hardening
3. Stock Movement audit trail
4. Companies / Sites
5. Receiving / Delivery
6. Suppliers improvements
7. Company Assets
8. Reusable Attachments
9. Knowledge Base / IT Docs
10. Reports
11. React setup and API bridge
12. Figma-to-React screen implementation

Do not add accounting, invoicing, payment, or ticketing/Tasklogger replacement features.

## Session 11: Login, Roles, and Command Center

Status:
- done

Implemented:
- Django auth login/logout
- protected operational pages
- prepared groups: Admin, Stock Manager, IT Support, Viewer
- BIM Nexus Command Center at `/`
- permission-aware Inventory link
- Django admin preserved

## Session 12: Login UI From Figma

Status:
- pending

Task:
Implement the BIM Nexus login screen from Figma.

Focus:
- keep Django auth form behavior
- update `templates/registration/login.html`
- match BIM Nexus black/white/orange branding
- keep responsive internal dashboard style

Do not change authentication logic.

## Session 13: Stock & Inventory Hardening

Status:
- pending

Task:
Align BIM Stock behavior with current operations without duplicating models.

Focus:
- inspect Product and ProductUnit first
- preserve SKU logic
- review status behavior before changing choices
- improve permissions where needed
- keep admin readable
- prepare API needs for future React screens

Avoid unrelated refactors.

## Session 14: Stock Movement Audit Trail

Status:
- pending

Task:
Add stock movement history as an audit trail.

Focus:
- movement type
- product
- stock unit where applicable
- quantity
- user
- date/time
- notes/reason

No accounting logic.

## Session 15: Companies / Sites

Status:
- pending

Task:
Add shared companies and sites.

Focus:
- company name
- site/branch
- contacts
- addresses
- notes
- active state
- reusable by delivery, receiving, movements, assets, and reports

## Session 16: Receiving / Delivery

Status:
- pending

Task:
Add dedicated receiving and delivery workflows.

Focus:
- receiving note number
- delivery note number
- supplier or company/site links
- receiver/deliverer/contact
- date
- item lines
- linked stock/products
- notes

Do not add invoices or payments.

## Session 17: Suppliers Improvements

Status:
- pending

Task:
Improve supplier operations beyond the current simple Supplier model.

Focus:
- admin usability
- search/filter needs
- supplier history through related stock and receiving data

Do not duplicate the existing Supplier model.

## Session 18: Company Assets

Status:
- pending

Task:
Add company-owned equipment tracking separate from stock inventory.

Focus:
- asset name/type
- brand/model
- serial number
- asset tag/barcode
- assigned employee/user
- department
- location
- status
- dates and notes where useful

Stock units remain inventory. Company assets are internal equipment in use.

## Session 19: Reusable Attachments

Status:
- pending

Task:
Add shared attachments.

Focus:
- file
- title
- notes
- uploaded by
- uploaded date
- related record
- admin inlines where useful

## Session 20: Knowledge Base / IT Docs

Status:
- pending

Task:
Add internal IT documentation.

Focus:
- title
- category
- tags
- content/body
- attachments
- active state
- created/updated audit fields

This is documentation only, not ticketing.

## Session 21: Reports

Status:
- pending

Task:
Prepare report structure.

Focus:
- current stock
- available stock
- damaged stock
- delivery history
- receiving history
- stock movement history
- supplier history
- company assets
- company/site history
- future Excel/PDF exports

## Session 22: React Operational UI

Status:
- pending

Task:
Introduce React for the main operational UI.

Focus:
- inspect current Django pages first
- keep Django admin
- add protected routes/pages
- use real APIs where data exists
- build reusable components
- use BIM Nexus black/white/orange branding
- implement dark collapsible sidebar, topbar, and main content layout
- include reusable cards, tables, forms, badges, filters, quick actions, and page headers
- desktop-first responsive design

Implement Figma screens only after inspecting the provided designs.
