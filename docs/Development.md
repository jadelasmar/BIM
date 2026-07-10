# Development

## Prerequisites

- Python
- Node.js and npm
- PowerShell on Windows

Use a fresh local virtual environment. Do not use checked-in `venv` or `.venv` folders.

## Recommended VS Code Extensions

Recommended extensions:

- Codex / OpenAI coding agent
- Python
- Pylance
- Django
- Djaneiro - Django Snippets
- Error Lens
- ESLint
- Prettier
- GitLens
- SQLite Viewer
- Tailwind CSS IntelliSense

Purpose:

- Python and Pylance are used for Django backend development.
- Django and Djaneiro help with Django syntax and snippets.
- ESLint and Prettier are used for frontend code quality and formatting.
- Tailwind CSS IntelliSense is used for Tailwind class autocomplete and validation.
- SQLite Viewer is used to inspect the local development database.
- GitLens is used to review file history and changes.
- Error Lens is used to show warnings and errors inline.
- Codex is used as the coding assistant.

When adding new required extensions, update `.vscode/extensions.json` and this section.

Project-level VS Code settings are stored in `.vscode/settings.json`. These settings define formatter behavior, ESLint validation, Tailwind language support, and ignored generated folders.

The default VS Code terminal profile opens PowerShell in `backend/` with the project `.venv` activated.

## Backend Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Frontend Setup

```powershell
cd frontend
npm install
npm run build
```

The build writes generated files to:

```text
backend/static/frontend/
```

Do not edit generated build files manually.

## Vite Dev Server

Terminal 1:

```powershell
cd frontend
npm run dev
```

Terminal 2:

```powershell
$env:BIM_VITE_DEV_SERVER = "http://127.0.0.1:5173"
cd backend
python manage.py runserver
```

## Common Commands

Backend checks:

```powershell
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Frontend build:

```powershell
cd frontend
npm run build
```

Whitespace check:

```powershell
git diff --check
```

## Environment Variables

Use `.env.example` as a reference for office setup. Django currently reads these values from the OS environment, service runner, or deployment script; it does not auto-load `.env` files.

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `BIM_EMAIL_BACKEND`
- `BIM_EMAIL_HOST`
- `BIM_EMAIL_PORT`
- `BIM_EMAIL_USE_TLS`
- `BIM_EMAIL_HOST_USER`
- `BIM_EMAIL_HOST_PASSWORD`
- `BIM_DEFAULT_FROM_EMAIL`
- `BIM_VITE_DEV_SERVER`

## Local Database

Local SQLite database:

```text
db.sqlite3
```

Do not commit local database files.

For first office testing, take a copy of `db.sqlite3` before entering real test data and after each test session. Also back up `backend/media/` if uploaded product images or files are used.

## Deployment Notes

- Set a real `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=false`.
- Configure allowed hosts for the target environment.
- Run `npm run build` before collecting/serving static assets.
- Configure static and media serving for production.
- Replace SQLite if production requires a server database.
- Use [Office Testing](OfficeTesting.md) for the first internal deployment checklist, user roles, database backups, and stock workflow smoke tests.
