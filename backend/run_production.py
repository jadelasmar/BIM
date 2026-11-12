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

# Must match the development default in bim/settings.py.
INSECURE_SECRET_KEY = "django-insecure-*85%i(ofy9ff93u84@&*-6)w$wy0b)9cr7ft^^rya@s=blcwao"


def check_production_config():
    """Return a list of problems that make this config unsafe to serve."""
    problems = []
    secret = os.environ.get("DJANGO_SECRET_KEY", "").strip()
    if not secret:
        problems.append("DJANGO_SECRET_KEY is missing from .env.production.")
    elif secret == INSECURE_SECRET_KEY or secret.startswith("django-insecure-"):
        problems.append("DJANGO_SECRET_KEY is the insecure development default; set a real secret.")
    if os.environ.get("DJANGO_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        problems.append("DJANGO_DEBUG is true; set DJANGO_DEBUG=False for production.")
    return problems


_problems = check_production_config()
if _problems:
    raise SystemExit(
        "Refusing to start BIM Nexus in production:\n  - " + "\n  - ".join(_problems)
    )

_email_backend = os.environ.get("BIM_EMAIL_BACKEND", "")
if not _email_backend or _email_backend.endswith((".console.EmailBackend", ".dummy.EmailBackend", ".locmem.EmailBackend")):
    print(
        "WARNING: no real email backend configured (BIM_EMAIL_BACKEND="
        f"{_email_backend or 'unset -> console'}). Password-setup emails will be "
        "printed to this log, not delivered. Set BIM_EMAIL_BACKEND/BIM_EMAIL_HOST/... "
        "in .env.production.",
        file=sys.stderr,
    )

if __name__ == "__main__":
    from waitress import serve

    from bim.wsgi import application

    host = os.environ.get("WAITRESS_HOST", "0.0.0.0")
    port = os.environ.get("WAITRESS_PORT", "8000")
    print(f"Starting waitress-serve on {host}:{port} "
          f"(DJANGO_DB_NAME={os.environ.get('DJANGO_DB_NAME')}, "
          f"DJANGO_DEBUG={os.environ.get('DJANGO_DEBUG')})", file=sys.stderr)
    serve(application, host=host, port=int(port))
