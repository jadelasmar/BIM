# BIM Nexus

BIM Nexus is an internal IT operations platform built for BIMPOS.

The current implemented module is BIM Stock, covering product definitions, physical stock units, stock entry, deliveries, suppliers, and operational visibility.

## Stack

- Backend: Django and Django REST Framework
- Frontend: React, Vite, Tailwind CSS
- Auth/admin/source of truth: Django
- Local database: SQLite
- Frontend build output: `backend/static/frontend/`

## Quick Start

Backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

Frontend build:

```powershell
cd frontend
npm install
npm run build
```

Open:

```text
http://127.0.0.1:8000/
```

## Documentation

Start here:

- [Documentation Index](docs/README.md)
- [Architecture](docs/Architecture.md)
- [Backend](docs/Backend.md)
- [Frontend](docs/Frontend.md)
- [Database](docs/Database.md)
- [Development](docs/Development.md)
- [Design System](docs/DesignSystem.md)
- [Roadmap](docs/Roadmap.md)
- [Coding Standards](docs/CodingStandards.md)
- [Code Map](docs/CodeMap.md)

The documentation describes the current codebase and should be updated when architecture, workflows, routes, models, or conventions change.
