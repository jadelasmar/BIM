# Frontend

The frontend is a React/Vite/Tailwind app under `frontend/`.

## Source Structure

```text
frontend/src/
  App.jsx
  main.jsx
  styles.css
  assets/
    brand/
  components/
    common/
  constants/
  hooks/
  pages/
    auth/
  routes/
  utils/
```

## Entry Flow

- `main.jsx` reads JSON from `#bim-nexus-initial-data`.
- `App.jsx` is a lightweight wrapper.
- `routes/AppRouter.jsx` selects the page based on Django-provided data and `currentPath`.

## Routing

React does not use a client router package. Route selection is centralized in `AppRouter.jsx`.

Important rendered routes:

- `/` Command Center
- `/inventory/` Inventory list
- `/inventory/products/new/` Add Product
- `/inventory/products/<id>/` Product Details
- `/inventory/receiving/new/` Receive Stock
- `/inventory/stock-units/new/` Add Unit
- `/inventory/deliveries/new/` Create Delivery
- `/operations/` Operations hub
- `/operations/receiving/` Receiving Records placeholder
- `/operations/receiving/<id>/` Receiving Record detail placeholder
- `/operations/deliveries/` Delivery Records placeholder
- `/operations/deliveries/<id>/` Delivery Record detail placeholder
- `/settings/` Settings
- `/accounts/login/` Login
- `/accounts/setup/<uid>/<token>/` Password setup

## Pages

Current dedicated page folder:

- `pages/auth/AuthPages.jsx`

Most operational pages currently live in `routes/AppRouter.jsx`. Split pages gradually when feature work touches them.

Good future page split targets:

- `pages/dashboard/CommandCenter.jsx`
- `pages/inventory/InventoryPage.jsx`
- `pages/inventory/ProductDetailsPage.jsx`
- `pages/inventory/AddProductPage.jsx`
- `pages/inventory/StockEntryPage.jsx`
- `pages/inventory/CreateDeliveryPage.jsx`

## Components

Reusable components:

- `components/common/Icon.jsx`
- `components/ui/Button.jsx`
- `components/ui/Card.jsx`
- `components/ui/Badge.jsx`
- `components/ui/Input.jsx`
- `components/ui/SearchBar.jsx`
- `components/ui/EmptyState.jsx`

Keep components small and extract only when reused or clearly feature-specific.

## Constants

- `constants/icons.js`: single Lucide icon source.
- `constants/statusStyles.js`: status badge classes and status icon metadata.
- `constants/uiRegistry.js`: frontend tones and workflow metadata.

## Hooks

- `hooks/useTheme.js`: theme storage key, current theme, and theme application.

## Utilities

- `utils/formatters.js`: count, date, and currency display helpers.

## Assets

Editable brand assets:

- `frontend/src/assets/brand/logo-primary.svg`
- `frontend/src/assets/brand/logo-white.svg`

Generated hashed copies appear under `backend/static/frontend/assets/` after build.

## State Management

There is no global state library. Current state is local React state inside pages/components.

Add context only when state is genuinely shared across separate feature areas.

## API Access

API URLs are provided through Django `initial_data.api`. Current fetch calls are inline in `AppRouter.jsx`.

Create a service layer when fetch logic becomes shared across multiple pages.
