# BIM Nexus Documentation

BIM Nexus is an internal IT operations platform built for BIMPOS. The current implemented business area is Inventory: product definitions, physical stock units, stock entry, deliveries, and operational visibility.

This documentation describes the current codebase. It is the source of truth for future development.

## Technology Stack

- Backend: Django, Django REST Framework
- Frontend: React, Vite, Tailwind CSS
- Auth/admin/source of truth: Django
- Local database: SQLite at `db.sqlite3`
- Frontend build output: `backend/static/frontend/`
- Uploaded media: `backend/media/`

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

## Folder Overview

```text
BIM/
  backend/       Django project, apps, templates, static, media
  frontend/      React/Vite/Tailwind source
  docs/          Project documentation
  README.md      Root project overview
  db.sqlite3     Local development database
```

## Documentation Index

- [Architecture](Architecture.md)
- [Code Map](CodeMap.md)
- [Design System](DesignSystem.md)
- [Backend](Backend.md)
- [Frontend](Frontend.md)
- [Database](Database.md)
- [Development](Development.md)
- [Office Testing](OfficeTesting.md)
- [Roadmap](Roadmap.md)
- [Coding Standards](CodingStandards.md)
