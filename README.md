# BIM Nexus

BIM Nexus is a Django-based internal IT operations platform.

Target architecture:
- Django is the backend, source of truth, auth layer, admin, and API provider.
- React is the planned main operational frontend.
- Tailwind CSS is the planned frontend styling system.
- Node.js is frontend build tooling only; it is not the BIM Nexus backend.

The repository's internal Django project package is currently named `bim`.
That package name is technical and does not change the product name shown to
users.

Business areas inside BIM Nexus should be added as focused Django apps/modules.
`bim_stock` is the first implemented module and is shown to users as BIM Stock.

## Internal Users

There is no public sign-up. Create internal users in Django admin with:
- unique email: `jad.alasmar@bimpos.com`
- active status

Email is required and cannot be removed from a user unless another valid, unique
email is entered.

New users start in the `Viewer` group automatically. Change their group in
Django admin when they need a higher role.

New users use a secure setup link and enter first name, last name, username, and password.
If username is left blank during setup, BIM Nexus uses the email name before `@`.
Users can log in with either their username or email after setup.
Each email must belong to one user only.

For account setup or reset, select the user in Django admin and run the
`Generate manual account setup links` action. Copy the generated link from the
Django admin message and send it manually from Outlook or another trusted email
client. This action does not use SMTP.

## Setup

Use a fresh local virtual environment and install the pinned requirements into
that environment. Do not use any existing checked-in `venv` or `.venv` folders.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

If `python manage.py ...` fails with `No module named 'django'`, Django is not
installed in the Python currently on your PATH. Activate the virtual environment
or run Django through that environment's Python:

```powershell
.\.venv\Scripts\python.exe manage.py check
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

## React Frontend

The protected Command Center at `/` is a React/Tailwind screen served through
Django auth. Django remains the backend, source of truth, admin, and login
system.

Install and build the frontend from `frontend/`:

```powershell
cd frontend
npm install
npm run build
```

The build writes Django-served assets to `static/frontend/`.

For React development with Vite hot reload, start Vite and point Django at it:

```powershell
cd frontend
npm run dev
```

In the PowerShell session running Django:

```powershell
$env:BIM_VITE_DEV_SERVER = "http://127.0.0.1:5173"
python manage.py runserver
```
