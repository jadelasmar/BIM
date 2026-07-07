# Office Testing And Deployment Checklist

BIM Nexus is ready for first internal office testing of BIM Stock workflows. This checklist is for a controlled internal test, not public production hosting.

## Scope

Included in the first office test:

- product catalogue and stock units
- Receiving and receiving correction/cancellation
- Delivery and delivery correction/cancellation
- Reservation, release, and cancel
- Issue and return from issue
- Repair and resolve
- Client Return from sold stock to available or repair
- Product detail movement history
- Command Center and inventory status counts

Not included yet:

- reports
- assets
- documents/forms
- client module
- supplier page beyond lookup/create support
- accounting, invoice, payment, tax, voucher, refund, credit note, or financial posting

## Must Do Before Office Test

1. Confirm the target PC/server has Python, Node.js/npm, and Git installed.
2. Create a fresh virtual environment outside committed folders.
3. Install backend requirements with `pip install -r backend\requirements.txt`.
4. Install frontend packages with `npm install` from `frontend\`.
5. Set office environment variables:
   - `DJANGO_SECRET_KEY` to a real random secret.
   - `DJANGO_DEBUG=false` for production-like office testing.
   - email variables if password setup links should be sent through SMTP.
6. Confirm the office host/IP is allowed in `backend/bim/settings.py`.
   Current allowed hosts are `192.168.1.101`, `localhost`, `127.0.0.1`, and `10.10.20.20`.
7. Run migrations.
8. Build frontend assets.
9. Create or confirm one superuser/admin account.
10. Confirm BIMPOS groups are created after migration:
    - Administrator
    - Operations Manager
    - IT Support
    - Viewer
11. Create the first office test users and assign groups.
12. Take a database backup before entering real office test data.
13. Keep the first test data set small and traceable.

## Can Wait Until Reports Phase

- report screens and exports
- advanced movement history screens
- dashboard trend analytics
- supplier/client full modules
- asset and document modules
- automated seed data fixtures
- production database migration away from SQLite, unless office concurrency requires it

## Environment Notes

The repository includes `.env.example` as a reference only. Django currently reads environment variables from the OS environment and does not auto-load `.env` files.

For PowerShell, set variables for the current terminal like this:

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-secret"
$env:DJANGO_DEBUG = "false"
```

For a persistent service, configure these variables in the service runner, Windows environment settings, or deployment script.

## Startup Commands

Production-like local office test:

```powershell
cd frontend
npm install
npm run build

cd ..\backend
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver 0.0.0.0:8000
```

Open from the server:

```text
http://127.0.0.1:8000/
```

Open from another office PC by replacing the address with the server IP, for example:

```text
http://10.10.20.20:8000/
```

Development hot-reload mode:

```powershell
cd frontend
npm run dev
```

In a second terminal:

```powershell
$env:BIM_VITE_DEV_SERVER = "http://127.0.0.1:5173"
cd backend
python manage.py runserver
```

Use built assets, not hot reload, for the office acceptance test unless actively debugging UI code.

## Database Backup Expectations

Local SQLite database file:

```text
db.sqlite3
```

Before office test data entry:

```powershell
Copy-Item ..\db.sqlite3 ..\backups\db-before-office-test.sqlite3
```

After each office test session:

```powershell
Copy-Item ..\db.sqlite3 ..\backups\db-after-office-test-YYYYMMDD.sqlite3
```

Also back up uploaded media if product images or uploaded files are used:

```powershell
Copy-Item -Recurse .\media ..\backups\media-after-office-test-YYYYMMDD
```

Do not commit database or media backup files.

## Recommended First Office Roles

Administrator:

- 1 IT owner only.
- Can access Django admin and all stock permissions.
- Creates users, checks permissions, and handles setup links.

Operations Manager:

- 1-2 office stock owners.
- Can create and correct operational stock records.
- Should perform receiving, delivery, reservation, issue, repair, and client return tests.

IT Support:

- 1 support user.
- Can view and change stock records but should not create new workflow records during acceptance unless explicitly testing support behavior.

Viewer:

- 1 read-only user.
- Confirms Command Center, inventory, records, and movement history visibility without write actions.

New non-superuser accounts default to Viewer. Move users to Operations Manager or IT Support explicitly in Django admin.

## Manual Smoke Test Checklist

Run this with a small set of test products and serial-numbered units.

### Login And Access

- Log in as Administrator.
- Create or confirm Operations Manager, IT Support, and Viewer users.
- Log in as Viewer and confirm write actions are not available.
- Log in as Operations Manager and confirm stock workflow actions are available.

### Product And Manual Unit

- Create a product with category, brand, model, barcode, and reorder level.
- Add one manual stock unit from `/inventory/stock-units/new/`.
- Confirm unit appears in inventory as available.
- Confirm Product Detail shows the manual add movement.

### Receiving

- Receive two serialized units for a product.
- Confirm a `RCV-YYYY-####` record is created.
- Confirm received units are available.
- Edit safe receiving fields: supplier/reference/date/notes/item cost/item notes.
- Cancel one test receiving record while units are unused.
- Confirm linked units become inactive and movement history records receiving cancellation.

### Delivery

- Create delivery from an available unit.
- Confirm a `DLV-YYYY-####` record is created.
- Confirm unit status becomes sold and no longer appears as available.
- Edit safe delivery fields: customer/receiver/date/notes/item notes.
- Cancel a test delivery while unit is untouched.
- Confirm unit returns to available and movement history records delivery cancellation.

### Reservation

- Create a reservation from an available unit.
- Confirm unit status becomes reserved.
- Confirm reserved unit cannot be selected for delivery.
- Release the reservation and confirm unit returns to available.
- Create another reservation and cancel it.

### Issue

- Create an issue from an available unit.
- Confirm unit status becomes issued.
- Confirm issued unit cannot be selected for delivery.
- Return the issue and confirm unit returns to available.

### Repair

- Create a repair from an available unit.
- Confirm unit status becomes repair.
- Resolve one repair to available.
- Resolve another repair to inactive.
- Confirm reserved, issued, and sold units are not accepted by Repair v1.

### Client Return

- Deliver an available unit so it becomes sold.
- From Delivery detail, use Create Client Return.
- Return one sold unit to available.
- Deliver another unit and return it to repair.
- Confirm the original delivery stays completed.
- Confirm no permanent ProductUnit returned status is created.

### Dashboard, Inventory, And Movement History

- Confirm Command Center counts reflect available/reserved/delivered/receiving changes.
- Confirm inventory filters work for available, reserved, issued, sold, repair, and inactive.
- Confirm Product Detail movement history shows receiving, delivery, reservation, issue, repair, and client return movements.
- Confirm recent receiving/delivery panels link only to real Receiving/Delivery records.

## Stop Conditions

Stop the office test and back up the database if any of these occur:

- a workflow changes the wrong ProductUnit status
- a record detail link opens the wrong record type
- a cancellation/release/return/resolve affects a unit changed by another workflow
- users can access actions outside their intended role
- product movement history is missing a completed stock operation

## Current Setup Gaps

- `ALLOWED_HOSTS` is hardcoded in settings. Update `backend/bim/settings.py` if the office server IP/hostname changes.
- The project does not auto-load `.env`; environment variables must be set by the shell or service runner.
- SQLite is acceptable for a small controlled office test, but concurrency and backup requirements should be reviewed before broader rollout.
- No automated seed data command exists yet. Use manual test data for the first office test.
