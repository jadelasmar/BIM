# BIM

BIM is a Django-based internal inventory / ERP-style project.

## Setup

Use a local virtual environment. Do not use the checked-in `venv` or `.venv`
folders.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Codex / VS Code

Codex is a developer tool, not a Python dependency for this Django project.
It should not be added to `requirements.txt`.

To use Codex on another PC with VS Code:

1. Install VS Code.
2. Install the Codex/OpenAI VS Code extension or CLI used by your account.
3. Sign in or configure the required API credentials.
4. Open this repository folder.
5. Install the project Python dependencies with `pip install -r requirements.txt`.

Project guidance for Codex sessions is in `docs/START-HERE.md`.
