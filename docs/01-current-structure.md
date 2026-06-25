# Current Structure

This file describes the current implementation.

## Project Layout

- Django project package: `bim`
- Active stock app: `bim_stock`
- Account helper app: `bim_accounts`
- React source: `frontend/src/`
- React build output: `static/frontend/`
- Shared Django theme assets: `static/bim/`
- React app shell template: `templates/bim/react_app.html`

Do not rename the Django package `bim` only for branding. User-facing UI should say BIM Nexus.

## Installed Extensions And Packages

Tracked backend packages in `requirements.txt`:
- `Django`
- `djangorestframework`
- `pillow`
- `asgiref`
- `sqlparse`
- `tzdata`

Django apps enabled in `INSTALLED_APPS`:
- Django built-ins: `admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`
- Third-party: `rest_framework`
- Project apps: `bim_accounts`, `bim_stock`

Tracked frontend packages in `frontend/package.json`:
- Runtime/build: `react`, `react-dom`, `vite`, `typescript`, `@vitejs/plugin-react`, `lucide-react`
- Styling toolchain: `tailwindcss`, `postcss`, `autoprefixer`

Developer workstation VS Code extensions currently used:
- `Codex - OpenAI's coding agent`
- `.NET Install Tool`
- `Auto Rename Tag`
- `Black Formatter`
- `C#`
- `C# Snippets`
- `C# XML Documentation Comments`
- `Path Intellisense`
- `Pylance`
- `Python`
- `Python Debugger`
- `Python Environments`
- `Python Indent`
- `SQLite Viewer`

Developer tools such as the Codex/OpenAI VS Code extension or CLI are not project runtime dependencies and should not be added to `requirements.txt`.

## Backend Apps

### `bim`

Owns:
- protected React app launcher
- Command Center payload
- main URLs
- shared UI registry for backend payload labels/icons/tones

### `bim_accounts`

Owns account helpers on top of Django auth:
- email-or-username login
- required unique email validation in admin
- email-only admin user creation
- admin-generated setup links
- first name, last name, username, password setup

### `bim_stock`

Owns BIM Stock:
- product hierarchy
- product definitions
- physical stock units
- suppliers
- delivery records
- inventory APIs
- Django admin for stock data

## Models

Current `bim_stock` models:
- `Category`
- `Brand`
- `ProductModel`
- `Product`
- `Supplier`
- `ProductUnit`
- `DeliveryRecord`
- `DeliveryItem`

Important conventions:
- `descript` is the internal product description/name field.
- `crdate` is created date/time.
- `isactive` is the soft-delete/active flag.
- SKU is auto-generated from category, brand, and model.
- `reorder_stock_level` is the single low-stock alert threshold.

`Product` calculated stock properties use active ProductUnit records:
- `total_units`
- `available_units`
- `reserved_units`
- `sold_units`
- `returned_units`
- `is_low_stock`
- `stock_alert_tone`

Current ProductUnit statuses:
- `available`
- `reserved`
- `sold`
- `returned`
- `inactive`

## Current Routes

Main protected React routes:
- `/` Command Center
- `/api/command-center/` refreshable Command Center JSON payload
- `/inventory/` BIM Stock list
- `/inventory/products/new/` Add Product
- `/inventory/products/<id>/` Product Details
- `/inventory/receiving/new/` Receive Stock
- `/inventory/stock-units/new/` Add Unit
- `/inventory/deliveries/new/` Create Delivery
- `/operations/` Operations hub
- `/operations/receiving/` Receiving Records placeholder
- `/operations/receiving/<id>/` Receiving detail placeholder
- `/operations/deliveries/` Delivery Records placeholder
- `/operations/deliveries/<id>/` Delivery detail placeholder
- `/suppliers/` Suppliers placeholder
- `/clients/` Clients placeholder
- `/assets/` Assets placeholder
- `/knowledge-base/` Knowledge Base placeholder
- `/settings/` Settings route, though theme is controlled from the global topbar

Auth/admin routes:
- `/accounts/login/`
- `/accounts/logout/`
- `/accounts/setup/<uid>/<token>/`
- `/admin/`

Stock API routes:
- `/api/stock/summary/`
- `/api/stock/products/`
- `/api/stock/products/<id>/`
- `/api/stock/product-units/`
- `/api/stock/product-units/<id>/`
- `/api/stock/categories/`
- `/api/stock/brands/`
- `/api/stock/models/`
- `/api/stock/suppliers/`
- `/api/stock/deliveries/`

Legacy Django stock template routes under `/stock/` were removed. Use React
`/inventory/` routes and Django admin for stock workflows.

## Implemented Features

Authentication:
- Django login/logout
- email-or-username login
- internal user creation through Django admin
- secure setup links
- prepared groups: Administrator, Operations Manager, IT Support, Viewer

React UI:
- Command Center
- BIM Stock list
- Product Details route/page with overview, stock-unit register, and workflow actions
- Add Product with inline Category/Brand creation and product image upload
- Receive Stock
- Add Unit
- Create Delivery
- Operations hub
- protected placeholders for future modules
- dark/light theme through `bim-nexus-theme`

Command Center:
- compact layout
- clickable KPI cards
- clickable System Overview cards
- compact Modules roadmap cards
- Recent Activity
- Recent Deliveries
- Recent Receiving
- topbar Refresh, Quick Add, theme toggle, user controls, logout

BIM Stock APIs:
- product list/create/detail/update
- stock unit list/create/detail/update
- delivery record list/create
- summary counts
- lookup endpoints, including Category/Brand create support for the Add Product UI

## Not Implemented Yet

- dedicated ReceivingRecord model
- stock movement audit model
- full Clients module
- full Suppliers page
- Assets module
- Knowledge Base module
- Reports module
- Forms/Documents module
- reusable attachments
