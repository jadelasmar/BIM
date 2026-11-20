# Digital signature and printable notes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Append-only drawn signatures on four record types plus a printable A4 operational note.

**Architecture:** New `RecordSignature` model keyed by record type + id; logic in `apps/stock/signatures.py` (never `services.py`); thin DRF views; React pad plus one `RecordNote` template component.

**Tech Stack:** Django 6 / DRF / Pillow (already installed), React 19, Tailwind 3.4. No new libraries.

**Spec:** `docs/superpowers/specs/2026-11-20-digital-signature-and-printable-notes-design.md`

## Global Constraints

- Never mutate `ProductUnit.status`, never write `StockMovement` from signature code.
- Permission constants in `constants.py`; check with `_require_perm` before validating the body.
- Image: PNG only, at most 204800 bytes, at most 1600x800, not blank.
- Note titles: "Receiving Note", "Delivery Note", "Assignment Note", "Client Return Note". Footer "Built for BIMPOS". No cost/price/invoice anywhere on the note.
- Keep `AppRouter.jsx` one file; new components live under `frontend/src/components/`.
- Do not touch `C:\Projects\BIM-Release`, `db_prod*`, `.env*` or `backend/static/frontend/`. Never deploy.
- Backend commands from `backend/`, frontend from `frontend/`. Focused tests until Task 5; full suite at the end.

## Review Focus

- A user without the record type's view permission guesses a signature id -> image route 403.
- Data URL with trailing whitespace/newlines, or bare base64 -> accepted; garbage -> 400, never 500.
- Signing a record id that does not exist -> 404, nothing written.
- Two signatures on one record -> both listed, oldest first.
- A record with ~60 items prints across pages with the header row repeated and no clipped rows.

---

### Task 1: Model, migration, constants, registry, creation function

**Files:** Modify `backend/apps/stock/models.py` (append `RecordSignature`), `constants.py`, `admin.py` (read-only); Create `backend/apps/stock/signatures.py`, migration `0045_recordsignature.py`; Test `backend/apps/stock/tests.py` (`SignatureModelTests`).

**Interfaces:**
- Produces: `RecordSignature` per spec; `signatures.SIGNABLE_RECORDS`; `signatures.validate_signature_png(data: str) -> bytes` (raises `django.core.exceptions.ValidationError`); `signatures.add_record_signature(*, record_type, record_id, image, signer_name="", role_label="", captured_by=None) -> RecordSignature` (`@transaction.atomic`; `LookupError` for a missing record, `ValidationError` for bad input; writes the "Signature added" `RecordChange` through `log_record_changes`); constants `VIEW_RECORD_SIGNATURE`, `ADD_RECORD_SIGNATURE`.

- [ ] **Step 1: Write failing tests** in `SignatureModelTests`: `test_valid_png_saved_with_history_row`, `test_oversize_rejected` (205000 bytes), `test_non_png_rejected`, `test_corrupt_png_rejected`, `test_blank_png_rejected`, `test_dimensions_rejected` (1700x100), `test_bare_base64_and_data_url_with_whitespace_accepted`, `test_unknown_type_rejected`, `test_missing_record_raises_lookup_error`, `test_cancelled_record_can_be_signed`, `test_no_stock_side_effects` (unit statuses, `StockMovement.count()`, record status and number unchanged), `test_history_failure_rolls_back` (patch `apps.stock.signatures.log_record_changes` to raise; no `RecordSignature` row remains).
- [ ] **Step 2:** `python manage.py test apps.stock.tests.SignatureModelTests` -> FAIL.
- [ ] **Step 3: Implement** model, constants, `signatures.py`, read-only admin (`has_add/change/delete_permission` False), then `python manage.py makemigrations bim_stock -n recordsignature` and `python manage.py migrate`.
- [ ] **Step 4:** Re-run -> PASS; `python manage.py check`; `python manage.py makemigrations --check --dry-run` clean.
- [ ] **Step 5: Commit** "Signatures: model, registry and append-only creation".

### Task 2: API endpoints, permissions, initial data

**Files:** Modify `api_views.py`, `api_urls.py`, `serializers.py`, `backend/apps/core/views.py` (permission flags, `api.signatures`); Test `tests.py` (`SignatureAPITests`, plus the write-endpoint matrix class).

**Interfaces:**
- Consumes: Task 1 functions and constants.
- Produces: `GET/POST /api/stock/signatures/`, `GET /api/stock/signatures/<pk>/image/`; JSON per spec; `initial_data.permissions.canAddSignature` / `canViewSignature`; `initial_data.api.signatures`.

- [ ] **Step 1: Write failing tests:** viewer GET list and image OK, POST `{}` 403; IT Support POST 201, response has no image bytes; anonymous list/create/image 401/403; user lacking the type's view perm gets 403 on list, image and create; PUT/PATCH/DELETE on both routes 405 as IT Support; validation errors 400; missing record 404; two signatures listed oldest first; image response `Content-Type: image/png`, `Cache-Control` contains `no-store`; roles: Viewer has `view_recordsignature` and not `add_`, IT Support has `add_` and no `delete_`; signature on a cancelled delivery works and stays listed; zero stock side effects through the API; `RecordChange` row visible via the record-history endpoint.
- [ ] **Step 2:** Run -> FAIL.
- [ ] **Step 3: Implement** thin views (permission checks first, then body; `ValidationError` -> 400, `LookupError` -> 404). Extend the matrix: add a `RECORD_ONLY` check that a user with only `change_productunit` is refused on `signatures/` and a user with `add_recordsignature` + `view_deliveryrecord` is not refused (400 on empty body, not 403).
- [ ] **Step 4:** Run `SignatureAPITests` and the matrix class -> PASS.
- [ ] **Step 5: Commit** "Signatures: API, permissions and initial data".

### Task 3: SignaturePad and SignatureSection

**Files:** Create `frontend/src/components/signature/SignaturePad.jsx`; Modify `frontend/src/routes/AppRouter.jsx` (add `SignatureSection`, render it directly above `<RecordHistory>` on the Receiving, Delivery, Issue and Client Return detail pages; add `#signature` to the four create-page redirects).

**Interfaces:**
- `SignaturePad` default export, props `{ onChange(dataUrlOrNull), disabled }`, imperative `clear()` and `undo()` via ref. Logical size 600x200, CSS width 100%, `touch-action: none`, white fill, `#111827` ink 2.5px round, retina-scaled, pointer capture.
- `SignatureSection({ data, type, id })` uses `data.api.signatures` and `data.permissions.canAddSignature`; presets role by `type` (receiving "Deliverer", delivery "Receiver", issue "Assigned to", client_return "Returned by"); after Save re-fetches the list and bumps the page's history reload key.

- [ ] **Step 1: Implement.** List shows image on a white box, name, role, "Captured by X on date time". Button label exactly "Collect signature". Save disabled while the pad is empty. Viewer sees the list only.
- [ ] **Step 2:** `npm run build` passes.
- [ ] **Step 3: Commit** "Signatures: drawing pad and detail page section".

### Task 4: Printable note

**Files:** Create `frontend/src/components/print/RecordNote.jsx`, `noteTypes.js`, `PrintPreview.jsx`; Modify `AppRouter.jsx` (Print button + `PrintPreview` on the four detail pages, items through `groupGenericItems`), `frontend/src/styles.css` (`@media print`).

**Interfaces:**
- `NOTE_TYPES[type] = { title, dateLabel, getNumber(record), getDate(record), party: [{label, get(record)}], getNotes(record) }` for `receiving`, `delivery`, `issue`, `client_return`.
- `RecordNote({ type, record, groupedItems, signatures })` renders the layout from the spec. `PrintPreview({ open, onClose, ...noteProps })` shows a full-screen white overlay with Print (`window.print()`) and Close; the sheet is 210mm wide, forced white and black regardless of theme. `@media print`: hide everything except the sheet, `@page { size: A4; margin: 12mm }`, `thead { display: table-header-group }`, `tr { break-inside: avoid }`.

- [ ] **Step 1: Implement.** Check: `grep -n -i "cost\|price\|invoice" frontend/src/components/print` returns nothing.
- [ ] **Step 2:** `npm run build` passes.
- [ ] **Step 3: Commit** "Notes: printable A4 operational note".

### Task 5: Docs, verification, backlog

- [ ] Update `Backend.md`, `Frontend.md` (replace the "no printed note" line), `Database.md`, `CodeMap.md`, `Roadmap.md`, `DesignSystem.md`, `Backlog.md` (item status and the Decisions line).
- [ ] Run `python manage.py check`, `makemigrations --check --dry-run`, `npm run build`, `python manage.py collectstatic --noinput`, `git diff --check`, full `python manage.py test`.
- [ ] Playwright on `http://127.0.0.1:8001/`: sign each of the four types (one at 390px), open each print view in dark theme, confirm white page and no cost/price. Commit docs, push, never deploy.
