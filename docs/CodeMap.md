# Code Map

This map describes where current BIM Nexus code lives and what each area owns.

## Root

```text
BIM/
  backend/
  frontend/
  docs/
  README.md
  db.sqlite3
```

## Backend

### `backend/manage.py`

Django command entry point. Run from `backend/`.

### `backend/bim/`

Configuration package:

- `settings.py`: installed apps, database, static/media, auth, email, Vite dev server, DRF settings
- `urls.py`: root URL includes
- `asgi.py`
- `wsgi.py`

### `backend/apps/core/`

Shared shell and Command Center:

- `views.py`: builds `initial_data`, renders React shell, serves Command Center JSON
- `urls.py`: protected shell routes
- `ui_config.py`: backend UI labels, icons, tones
- `templatetags/vite.py`: Vite manifest/dev-server asset loading

Important routes:

- `/`
- `/api/command-center/`
- `/inventory/`
- `/inventory/products/new/`
- `/inventory/products/<id>/`
- `/inventory/receiving/new/`
- `/inventory/stock-units/new/`
- `/inventory/deliveries/new/`
- `/operations/`
- `/operations/receiving/`
- `/operations/deliveries/`
- `/suppliers/`
- `/clients/`
- `/assets/`
- `/knowledge-base/`
- `/settings/`

### `backend/apps/accounts/`

Account layer on top of Django auth:

- `admin.py`: admin user creation/editing behavior
- `backends.py`: email-or-username authentication backend
- `forms.py`: login and password setup forms
- `signals.py`: default group assignment
- `utils.py`: setup-link helper
- `views.py`: login/setup React page data
- `urls.py`: login/setup routes

Important routes:

- `/accounts/login/`
- `/accounts/setup/<uidb64>/<token>/`

### `backend/apps/stock/`

BIM Stock business app:

- `models.py`: stock models
- `admin.py`: staff-friendly admin
- `serializers.py`: DRF serializers
- `api_views.py`: stock APIs
- `api_urls.py`: stock API routing
- `selectors.py`: reusable read queries for dashboards/app shell
- `constants.py`: app label and permission strings
- `roles.py`: prepared stock-related groups and permissions
- `tests.py`: backend and source-inspection tests
- `migrations/`: preserved migration history

Important API routes:

- `/api/stock/summary/`
- `/api/stock/products/`
- `/api/stock/products/<id>/`
- `/api/stock/product-units/`
- `/api/stock/product-units/<id>/`
- `/api/stock/deliveries/`
- `/api/stock/suppliers/`
- `/api/stock/brands/`
- `/api/stock/models/`
- `/api/stock/categories/`

## Templates And Static

### `backend/templates/bim/react_app.html`

Minimal React mount template. It:

- writes `initial_data` into the page
- loads Vite dev assets when `BIM_VITE_DEV_SERVER` is set
- otherwise loads generated Vite assets through `manifest.json`

### `backend/static/frontend/`

Generated Vite output. Do not edit manually.

Expected generated files:

- `manifest.json`
- hashed JS/CSS/assets under `assets/`

### `backend/media/`

Uploaded media root. Product images currently use the model upload path `products_images/`.

## Frontend

### `frontend/src/main.jsx`

React entry point. Reads initial data from `#bim-nexus-initial-data` and mounts `<App />`.

### `frontend/src/App.jsx`

Lightweight app entry. Delegates rendering to `routes/AppRouter.jsx`.

### `frontend/src/routes/AppRouter.jsx`

Current main operational UI implementation:

- route table
- app shell
- sidebar/topbar
- Command Center
- Inventory
- Product Details
- Add Product
- Receive Stock/Add Unit
- Create Delivery
- placeholder pages
- shared UI pieces not yet split out

This file is the main remaining frontend split target.

### `frontend/src/pages/auth/AuthPages.jsx`

React login and password setup pages. Django still validates and posts the forms.

### `frontend/src/components/common/Icon.jsx`

Registry-backed icon component.

### `frontend/src/components/ui/`

Small reusable UI foundation:

- `Button.jsx`: shared action button variants and sizes
- `Card.jsx`: shared panel/card pieces
- `Badge.jsx`: status/tone badge display
- `Input.jsx`: shared input styling
- `SearchBar.jsx`: shared search field with icon
- `EmptyState.jsx`: shared empty panel display
- `index.js`: UI component exports

### `frontend/src/constants/`

- `icons.js`: single Lucide icon source
- `statusStyles.js`: status badge styles and status icon metadata
- `uiRegistry.js`: tone classes and workflow metadata

### `frontend/src/hooks/useTheme.js`

Shared dark/light theme helpers.

### `frontend/src/utils/formatters.js`

Display formatting helpers for counts, dates, and currency.

### `frontend/src/assets/brand/`

Editable logos:

- `logo-primary.svg`
- `logo-white.svg`

### `frontend/src/styles.css`

Tailwind directives, theme CSS variables, and light-theme overrides.

## Important Flows

### Protected App Load

```text
GET /
  -> apps.core.views.module_launcher
  -> builds initial_data
  -> renders backend/templates/bim/react_app.html
  -> React mounts from frontend/src/main.jsx
  -> AppRouter chooses page from currentPath
```

### Login

```text
GET/POST /accounts/login/
  -> apps.accounts.views.login_view
  -> Django validates credentials
  -> React renders login page from page data
```

### Product Creation

```text
React Add Product page
  -> POST /api/stock/products/
  -> ProductSerializer
  -> Product.save() generates SKU
```

### Delivery Creation

```text
React Create Delivery page
  -> POST /api/stock/deliveries/
  -> DeliveryRecordSerializer.create()
  -> creates DeliveryRecord and DeliveryItem rows
  -> marks selected ProductUnit rows sold
```

## Main Technical Debt

- `frontend/src/routes/AppRouter.jsx` is still large.
- Frontend API calls are inline.
- More UI patterns should move into `components/ui/` only when repeated by current screens.
- Full Receiving Records need dedicated models.
- Supplier/client/assets/report modules are placeholders or partial.
- `Product.image` still uploads to `products_images/`.
