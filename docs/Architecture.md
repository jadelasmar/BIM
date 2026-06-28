# Architecture

BIM Nexus is a Django + React application. Django owns the backend, source of truth, authentication, admin, APIs, templates, static/media configuration, and local development commands. React owns the operational UI.

## Application Flow

```text
Browser
  -> Django URL routing
  -> Django auth/session checks
  -> backend/templates/bim/react_app.html
  -> React initial data in #bim-nexus-initial-data
  -> frontend/src/main.jsx
  -> frontend/src/App.jsx
  -> frontend/src/routes/AppRouter.jsx
  -> Django REST APIs
  -> Django models
  -> db.sqlite3
```

## Responsibilities

### Django

- Settings and root URLs in `backend/bim/`
- First-party apps in `backend/apps/`
- Session authentication and CSRF
- Django admin
- Permissions and role preparation
- Models and migrations
- API views and serializers
- React mount template
- Static/media configuration

### React

- Operational screens
- Client-side route selection from `initialData.currentPath`
- Auth screens rendered from Django-provided page data
- UI constants, status styles, icons, and theme behavior
- API calls to Django endpoints

## Build Pipeline

Editable React source lives in `frontend/src/`.

Vite builds directly into:

```text
backend/static/frontend/
```

That folder is generated output. Do not edit files there manually.

Django loads generated assets through:

```text
backend/static/frontend/manifest.json
backend/apps/core/templatetags/vite.py
backend/templates/bim/react_app.html
```

For Vite hot reload, set `BIM_VITE_DEV_SERVER` before running Django.

## Stable Folder Structure

```text
BIM/
  backend/
    manage.py
    requirements.txt
    bim/
    apps/
      accounts/
      core/
      stock/
    templates/
    static/
    media/
  frontend/
    src/
    package.json
    vite.config.js
    tailwind.config.js
  docs/
```

## Route Ownership

- Root app shell routes are in `backend/apps/core/urls.py`.
- Account routes are in `backend/apps/accounts/urls.py`.
- Stock API routes are in `backend/apps/stock/api_urls.py`.
- React page selection is centralized in `frontend/src/routes/AppRouter.jsx`.

