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
- SQLite Viewer
- Tailwind CSS IntelliSense

Purpose:

- Python and Pylance are used for Django backend development.
- Django and Djaneiro provide Django template and project support.
- Error Lens surfaces editor diagnostics inline.
- ESLint and Prettier are available for frontend editing, but are not run automatically because the project does not currently include their configuration.
- SQLite Viewer supports inspection of the local development database.
- Tailwind CSS IntelliSense is used for Tailwind class autocomplete and validation.
- Codex is used as the coding assistant.

Ruff is not currently configured as a project tool. Add it only with project configuration and a documented verification command; do not enable formatter-on-save globally.

When adding new required extensions, update `.vscode/extensions.json` and this section.

Project-level VS Code settings are stored in `.vscode/settings.json`. These settings keep format-on-save disabled, select the project virtual environment, define Tailwind language support, and hide generated folders.

VS Code terminals open in `backend/` and use the project `.venv` through terminal environment variables. Python extension auto-activation is disabled so new terminals do not print an activation command.

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

When Django runs with `DEBUG=true`, the Vite manifest is re-read for each rendered page so a new `npm run build` is picked up without restarting Django. Production mode caches the manifest for efficiency and should be restarted after deploying a new frontend build.

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

## Automatic Migrations After Pull

This repository includes `.githooks/post-merge`. After a successful merge-based `git pull`, the hook automatically runs existing Django migrations with:

```powershell
.\.venv\Scripts\python.exe backend\manage.py migrate --noinput
```

Activate the versioned hooks once for each local clone:

```powershell
git config --local core.hooksPath .githooks
```

The hook resolves the repository root internally, so it does not depend on the terminal's current directory. It requires the local interpreter at `.venv/Scripts/python.exe`.

If the virtual environment is missing, the hook prints a setup error and exits non-zero. If a migration fails, it prints a prominent failure message and exits non-zero so an outdated database does not go unnoticed. A failing `post-merge` hook cannot undo a pull that Git has already merged successfully; resolve the reported migration error before starting BIM Nexus.

The hook only applies migration files already committed to the repository. It never runs `makemigrations` and never creates migration files automatically.

`post-merge` runs for merge-based pulls only. Rebase-based pulls do not invoke this hook and remain outside the current automatic-migration scope.

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
- `BIM_ADMIN_EMAIL`: recipient for login-page account access requests; defaults to `jad.alasmar@bimpos.com` when unset.
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
