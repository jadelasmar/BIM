"""
Production launcher for BIM Nexus.

Unlike `manage.py runserver` (which loads backend/.env via settings.py),
this script explicitly loads backend/.env.production - with overwrite=True,
so it wins even if the process already has stray DJANGO_* variables set -
before Django is imported. That guarantees the deployed service uses the
production DEBUG/ALLOWED_HOSTS/DB_NAME regardless of what backend/.env
currently contains.

Usage (from backend/):
    python run_production.py

One-time setup before first deploy - create/migrate the production database
(db_prod.sqlite3) without starting the server. Run from backend/:
    Windows (PowerShell):
        $env:DJANGO_DB_NAME="db_prod.sqlite3"; python manage.py migrate
    Windows (cmd.exe):
        set DJANGO_DB_NAME=db_prod.sqlite3 && python manage.py migrate
"""
import os
import sys
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env.production"

if not ENV_FILE.exists():
    raise SystemExit(
        f"{ENV_FILE} not found - refusing to start without a production config."
    )

environ.Env.read_env(ENV_FILE, overwrite=True)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bim.settings")

if __name__ == "__main__":
    from waitress import serve

    from bim.wsgi import application

    host = os.environ.get("WAITRESS_HOST", "0.0.0.0")
    port = os.environ.get("WAITRESS_PORT", "8000")
    print(f"Starting waitress-serve on {host}:{port} "
          f"(DJANGO_DB_NAME={os.environ.get('DJANGO_DB_NAME')}, "
          f"DJANGO_DEBUG={os.environ.get('DJANGO_DEBUG')})", file=sys.stderr)
    serve(application, host=host, port=int(port))
