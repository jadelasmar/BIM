# Digital signature and printable record notes — design

Date: 2026-11-20. Backlog item: "Operations | Digital signature and printable Receiving / Delivery / Issue / Client Return notes".
Decisions were fixed in the request (no review between steps); this spec records them plus the choices made to fill gaps.

## Goal

A person can collect a signature on a Receiving, Delivery, Assignment (Issue) or Client Return record after it exists, and print a one-page A4 operational note (or save it as PDF) that carries the signature. Nothing about stock changes.

## Non-goals

No PDF library, no new npm/pip dependency, no prices/costs on the note (it is an operational note, never an invoice), no signature edit/replace/delete, no glass restyle, no signing of Reservation, Repair, Removal or Upgrade records (a one-line addition later).

## Data model (migration 0045)

`RecordSignature` (app label `bim_stock`):

| field | notes |
|---|---|
| `record_type` | CharField(30); one of `receiving`, `delivery`, `issue`, `client_return` (same slugs as `RecordChange` and record history) |
| `record_id` | PositiveIntegerField; indexed together with `record_type` |
| `record_number` | CharField(32), copied at signing time like `RecordChange` |
| `signer_name` | CharField(150), printed name, optional (blank allowed) |
| `role_label` | CharField(50), optional, e.g. Deliverer / Receiver / Assigned to / Returned by |
| `image` | BinaryField, validated PNG bytes, at most 200 KB (204800 bytes) |
| `signed_at` | DateTimeField(default=timezone.now) |
| `captured_by` | FK to user, SET_NULL |

Keyed by type + id (no FK), like `RecordChange`, so a new type is one entry in a registry. Several signatures per record are allowed (e.g. deliverer and receiver). Append-only: no update and no delete through the API; the Django admin registration is read-only (no add/change/delete). Django still creates the `change_`/`delete_` model permissions but nothing uses them; IT Support lacks `delete_` by the existing role rule.

## Registry

`apps/stock/signatures.py` holds `SIGNABLE_RECORDS = {slug: SignableRecord(model, number_attr, view_perm, label)}` for the four types, `add_record_signature(...)` and `validate_signature_png(data)`. It is separate from `services.py` on purpose: it never calls stock services and never touches `ProductUnit` or `StockMovement`.

## Validation (server)

- `image` is a `data:image/png;base64,...` string (bare base64 also accepted). Decoded size 1..204800 bytes, else 400.
- Must open with Pillow (`Image.open` + `verify`), format `PNG`, width <= 1600, height <= 800, else 400.
- Must not be blank: flattened onto white it needs at least one non-white pixel, else 400.
- `signer_name` max 150, `role_label` max 50, both stripped, both optional.
- Record must exist and be of a signable type; unknown type 400, missing record 404. A cancelled/inactive record can still be signed and its signatures stay visible.

## API

- `GET /api/stock/signatures/?type=delivery&id=4` -> list, oldest first: `id, record_type, record_id, record_number, signer_name, role_label, signed_at, captured_by` (display name), `image_url`. Never returns image bytes. Needs `VIEW_RECORD_SIGNATURE` and the record type's own view permission.
- `POST /api/stock/signatures/` body `{type, id, image, signer_name, role_label}` -> 201, same shape. Needs `ADD_RECORD_SIGNATURE` and the record type's view permission (the user must be able to see the record). It does not need `CHANGE_PRODUCT_UNIT`: convention 2's pairing exists for writes that mutate units, and this one touches none (documented deliberate exception). The permission check runs before validation, so a Viewer always gets 403. The whole write is `transaction.atomic`.
- `GET /api/stock/signatures/<id>/image/` -> `image/png`, `Cache-Control: private, no-store`, same permission pair as the list. Unauthenticated -> 401/403.
- No PUT/PATCH/DELETE routes (DRF answers 405).
- History: each signature writes one `RecordChange` row, `field_label="Signature added"`, `old_value=""`, `new_value="<signer or 'unnamed'> (<role or 'no role'>)"`, `changed_by=captured_by`, in the same atomic block. `RecordHistoryAPIView` already serves `receiving`, `delivery`, `issue` and `client_return`, so it needs no change.

## Permissions

Constants `VIEW_RECORD_SIGNATURE`, `ADD_RECORD_SIGNATURE` in `constants.py`. `roles.py` already grants Viewer every `view_*` and IT Support everything except `delete_*`, and `post_migrate` re-prepares the groups, so no role code changes; tests pin the result (Viewer views not adds, IT Support adds, nobody has delete). `initial_data.permissions` gains `canAddSignature` and `canViewSignature`; `initial_data.api` gains `signatures`.

## Frontend

- `components/signature/SignaturePad.jsx`: canvas + pointer events (`touch-action: none`), pointer capture, Clear, Undo (per stroke), logical size fixed and scaled to container width (works at 390px), white background and dark ink in both themes (inline colours, not theme tokens), `toDataURL("image/png")`, reports empty as `null`. No library.
- `SignatureSection` (in `AppRouter.jsx`, directly above `RecordHistory` on the four detail pages, `id="signature"`): lists existing signatures read-only (image, printed name, role, captured by/time); if `canAddSignature`, a "Collect signature" button opens a form: name, role (preset per type: Receiving -> Deliverer, Delivery -> Receiver, Issue -> Assigned to, Client Return -> Returned by; free text allowed), the pad, Save. Shown for cancelled records too.
- Post-create success flow: the create pages already redirect to the detail page; the redirect gains `#signature` so the person lands on the section. Nothing blocks or delays creation.
- Print: a Print button on the four detail pages opens `PrintPreview`, a full-screen white overlay holding the A4 sheet with Print / Close buttons. Print calls `window.print()`. `@media print` hides everything except the sheet, sets `@page { size: A4; margin: 12mm }`, white background and black text regardless of theme.
- Template: ONE component, `components/print/RecordNote.jsx`, renders header (logo-primary.svg, note title, record number, date), party block, items table, notes, signature block (image, printed name, role, captured by / time; an empty signature line when unsigned) and footer "Built for BIMPOS". Per-type content lives in a small config `NOTE_TYPES` in `components/print/noteTypes.js`: title, date label, party rows, notes picker. Restyling = edit `RecordNote.jsx` only; adding a type = one `NOTE_TYPES` entry plus a Print button.
- Items use the existing `groupGenericItems` (real serials one line each; generic units of one product one line with a count and "no serial"). The note shows no cost, price, sale price, invoice number, PO number or supplier invoice amount. Decision: even reference numbers like invoice/PO are omitted so the note is unambiguously not an invoice.
- `AppRouter.jsx` stays one file. `tests.py` asserts on it by slicing between function names, so the new components go into separate leaf files under `components/` (no test slices cover them, and they depend on nothing inside `AppRouter`), and only thin wiring (`SignatureSection`, Print button) is added to `AppRouter.jsx`.
- Design: existing solid Card/Button/Input styles; screen UI supports dark theme; the pad and the print sheet are always white.
- Convention 5 (UI token sync): no new module or status, so no `ui_config.py` / `uiRegistry.js` change. Convention 7 (field order): no workflow form changes. Convention 8: the signature writes a history row, as above. Global search and Command Center: a signature is a child of an existing record, not a record type, so no new search group or dashboard provider.
- Clickable-row rule: no new lists/rows of records are introduced; signature rows are not records.

## Testing

Backend focused tests: Viewer refused on POST (and allowed to view), append-only (PUT/PATCH/DELETE 405, admin read-only), size/format/blank/dimension validation, unauthenticated refused on list/create/image, signature on a cancelled record, zero side effects (unit statuses, `StockMovement` count, record status unchanged), history row written, rollback when history logging fails, role permissions pinned. The write-endpoint matrix test picks up the new POST route automatically (Viewer 403, anonymous 401/403); a record-only pairing check is added. Frontend: `npm run build`, then Playwright.

## Risks and decisions

- BinaryField in SQLite is fine at this size and a database backup carries the signatures; the 200 KB cap keeps rows small.
- A drawn image is evidence that a person drew something, not a cryptographic signature; the docs say so.
- Print relies on the browser print dialog; long item lists repeat the table header and rows avoid page breaks.
