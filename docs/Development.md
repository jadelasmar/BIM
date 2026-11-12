# Development

## Prerequisites

- Python
- Node.js and npm
- PowerShell on Windows

Use a fresh local virtual environment. Do not use checked-in `venv` or `.venv` folders.

## Recommended VS Code Extensions

Recommended extensions:

- Claude Code
- Codex / OpenAI coding agent
- Python
- Pylance
- Django
- Error Lens
- SQLite Viewer
- Tailwind CSS IntelliSense

Purpose:

- Python and Pylance are used for Django backend development.
- Django provides Django template and project support.
- Error Lens surfaces editor diagnostics inline.
- ESLint and Prettier are intentionally not recommended: the project has no configuration for them. Add them back to `.vscode/extensions.json` together with their config.
- SQLite Viewer supports inspection of the local development database.
- Tailwind CSS IntelliSense is used for Tailwind class autocomplete and validation.
- Claude Code and Codex are used as coding assistants. Claude Code project tooling (plugins, MCP servers, hooks) is configured in `.claude/settings.json`, `.mcp.json` and `.claude/hooks/`.
- The Claude Code LSP plugins (`typescript-lsp`, `pyright-lsp`) need their language servers installed separately (`typescript-language-server`, `pyright`).

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

Django reads these values from the OS environment, or from `backend/.env` if present (loaded automatically via `django-environ`; real deployments should set actual OS env vars instead of shipping a `.env` file).

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`: comma-separated, e.g. `localhost,127.0.0.1,192.168.1.101`.
- `DJANGO_DB_NAME`: SQLite filename, lives at repo root; defaults to `db.sqlite3`.
- `BIM_EMAIL_BACKEND`
- `BIM_EMAIL_HOST`
- `BIM_EMAIL_PORT`
- `BIM_EMAIL_USE_TLS`
- `BIM_EMAIL_HOST_USER`
- `BIM_EMAIL_HOST_PASSWORD`
- `BIM_DEFAULT_FROM_EMAIL`
- `BIM_ADMIN_EMAIL`: recipient for login-page account access requests; defaults to `jad.alasmar@bimpos.com` when unset.
- `BIM_VITE_DEV_SERVER`

## Database Concurrency

Production runs under Waitress with several threads on one SQLite file. `select_for_update()` does nothing on SQLite, so `backend/bim/settings.py` sets `OPTIONS = {"transaction_mode": "IMMEDIATE", "timeout": 20}`: every `transaction.atomic` block (all of `services.py`) takes the write lock when it starts, so overlapping workflows queue instead of racing, and the second one re-reads the unit, sees its new status and is refused with a normal validation error (HTTP 400) rather than "database is locked". WAL mode is deliberately not enabled: `deploy\rollback.ps1` copies only the main `.sqlite3` file, which would lose or corrupt `-wal`/`-shm` data.

## Production Launcher Checks

`backend/run_production.py` refuses to start when `DJANGO_SECRET_KEY` is missing or still the insecure development default, or when `DJANGO_DEBUG` is true. It prints a warning at start-up when `BIM_EMAIL_BACKEND` is unset or console/dummy/locmem, because password-setup emails would then be printed to the log instead of delivered.

## Local Database

Local SQLite database:

```text
db.sqlite3
```

Do not commit local database files.

For first office testing, take a copy of `db.sqlite3` before entering real test data and after each test session. Also back up `backend/media/` if uploaded product images or files are used.

`/media/` (uploaded product images) requires a logged-in session: `backend/bim/urls.py` wraps the media view in `login_required`, so anonymous requests are redirected to the login page. Images in the app still load because the browser sends the session cookie with each image request.

## UI smoke testing (Playwright)

The project `.mcp.json` registers a Playwright MCP server so Claude Code can drive the app in a browser. `db.sqlite3` is the local development database, so Playwright may run against the normal dev server at `http://127.0.0.1:8000/` and create or edit records there. Log in yourself in the Playwright browser window; Claude does not create users or store credentials. Never point it at production (`db_prod.sqlite3`); production changes only go out through a build and release.

Optionally, to keep dev data untouched, run a second dev server against a throwaway database. `DJANGO_DB_NAME` selects the SQLite filename at the repo root (see `backend/bim/settings.py`):

```powershell
cd backend
$env:DJANGO_DB_NAME = "smoke_ui.sqlite3"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

Point Playwright at `http://127.0.0.1:8001/`. Migrating the throwaway file also creates the Administrator / IT Support / Viewer groups. `*.sqlite3` is already in `.gitignore`, so the file is never committed; delete it any time to reset. Create the test user and enter its password yourself; Claude should not create users or store credentials. If you want Vite hot reload, also set `BIM_VITE_DEV_SERVER` as described above.

The first time Claude Code opens this project it asks you to approve the project-scoped `playwright` and `context7` MCP servers (`claude mcp list` shows them as "Pending approval" until then). On native Windows they are wrapped as `cmd /c npx ...`, because Claude Code cannot spawn `npx` directly there.

## Deployment Notes

- Set a real `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=false`.
- Configure allowed hosts for the target environment.
- Run `npm run build` before collecting/serving static assets.
- Configure static and media serving for production.
- Replace SQLite if production requires a server database.
- Use [Office Testing](OfficeTesting.md) for the first internal deployment checklist, user roles, database backups, and stock workflow smoke tests.

### Release checkout

`C:\Projects\BIM-Release` is a separate clone of the same repository used for production. It holds `db_prod.sqlite3` and runs the scripts below. Develop and test in `C:\Projects\BIM`. Once a change is verified, commit and push it to GitHub, then run `deploy.bat` in `BIM-Release`. It is a thin wrapper (with `rollback.bat`) around the versioned `deploy\deploy.ps1`, which pulls from GitHub, so nothing is copied from `BIM` directly and unpushed work never reaches production.

### Production deploy scripts

The scripts live in `deploy/` and are run on the production server (see `backend/run_production.py` for how the app itself runs):

- `deploy\deploy.ps1` backs up `db_prod.sqlite3` to `backend\backups\` using SQLite's online backup, verifies the copy with `PRAGMA integrity_check` and stops if it is not valid. The verified backup is also copied to `\\hostserver\Technical Dep\Jad\BIM Nexus` and checked by hash; if the share is unreachable or the copy does not match, the deploy stops before changing anything. It then copies `backend\media` to a `media` folder on the same share with `robocopy /E` (adds and updates files, never deletes from the share; robocopy exit codes 0-7 are success, 8 or more stops the deploy; skipped with a message if `backend\media` does not exist). Only after the database copy is confirmed does it delete older timestamped backups, locally and on the share, keeping the newest `$KeepBackups` (default 1, set at the top of the script). `db_prod_prerollback_*` safety copies are never deleted. Then it runs `git pull --ff-only`, rebuilds the frontend, runs `collectstatic` and `migrate`, restarts the `BIMNexus` service, then checks that the site answers and serves the new frontend build. It stops on the first failure and prints which step failed.
- `deploy\rollback.ps1` stops the service, lets you pick a commit and/or a database backup to go back to, and starts it again. Before restoring a backup it saves the current database as `db_prod_prerollback_<timestamp>.sqlite3`, so a restore never destroys data.

`db_prod.sqlite3` and `backend\backups\` are ignored by git and are never touched by `git pull`. The share copy protects against a disk failure on the server. The deploying Windows account needs write access to the share.
- `deploy\grant-restart-permission.ps1` is a **one-time** setup, run in an Administrator PowerShell. It lets the deploying Windows account start and stop only the `BIMNexus` service, so `deploy.ps1` finishes without an elevated prompt. Without it the deploy completes every step except the restart, which then needs an Administrator window.

