# Generic (no-serial) units: flag, quantity pickers, grouped display

Date: 2026-11-19 · Status: decided by the requester up front, no review round (the requester chose to skip reviews between spec, plan and implementation).

## Problem

Units received without a typed serial get an auto-made serial built in the frontend:

- Receive Stock: `SKU-batch-line-NNN` (`buildGeneratedSerial` in `StockEntryPage`).
- Add Unit: `SKU-batch-NNN` (`createProductUnits`).

`batch` is the last six digits of `Date.now()`. These serials are stored exactly like real ones, so every unit picker (Delivery, Reservation, Issue/Assignment, Repair, Removal, Client Return) makes the user click generic units one at a time, and every detail page lists them one line each.

## Goals

1. Record, on the unit, whether its serial was auto-made (`ProductUnit.serial_is_generated`).
2. In every unit picker, offer generic units of a product as one row with a quantity input and "N available"; real-serial units stay individual rows.
3. Show generic units of one product as one line ("N units, no serial") on record detail pages.
4. Keep the Stock Units view/CSV listing every unit, with a generated/real column.

## Non-goals / anti-goals

- **No change to `services.py`** (workflow functions, `StockMovement`, locking). It has a zero diff in this feature. The picker resolves a quantity to specific unit ids before submitting; the services see an ordinary `unit_ids` list.
- No new libraries, no splitting `AppRouter.jsx` (convention 4).
- No behaviour change for real serials, scanning, or any status rule.
- No printed notes exist in the app (no print view, no PDF, no print CSS), so decision 6's "printed note" part has nothing to change. If one is added later it must reuse the grouping helper.

## Decisions

### D1. The flag, and where serials are generated

`ProductUnit.serial_is_generated = BooleanField(default=False)`. It is **read-only in the API** (a client cannot set it), so it can only be set by the backend generating the serial.

Generation moves to the backend (new `apps/stock/serials.py`, pure helpers: no status changes, no movements):

| Creation path | How the serial is generated | Flag |
|---|---|---|
| Receive Stock (`POST receiving-records/`) | Item input gets `auto_serial_count` (int, default 0). `serial_numbers` carries only the typed/scanned serials; `len(serial_numbers) + auto_serial_count` must equal `quantity`. `ReceivingRecordSerializer.create` generates the missing serials (`SKU-batch-LL-NNN`) and passes the full list to `create_receiving_record` unchanged. | set to True for exactly those serials, in the same `transaction.atomic()` as the create |
| Add Unit (`POST product-units/`) | `serial_number` becomes optional on create. Blank/missing → generated (`SKU-batch-NNN`). The frontend sends the typed serial when it has one, else omits it. Blank on update is still rejected. | True when generated |
| Client-owned repair intake (`_create_client_owned_units`) | Serial is mandatory and typed | False (real) |
| Django admin add | Serial typed | False |
| `seed_demo_data` | Passes demo serials (`DEMO-SKU-001`) to `create_receiving_record`; these are fixtures standing in for real serials | False |

Why not touch `create_receiving_record` to set the flag? Requirement 5 forbids changing the services. Setting the flag in the serializer, in the same transaction that creates the units, from the same function that generated the serials, cannot drift. If a frontend-only approach had been needed the reason would be recorded here; it is not.

Generated serials are guaranteed unique at generation time (checked against existing serials; the batch digits are bumped on a collision). The service's existing duplicate check remains the final guard.

**Serial edited later.** When a person replaces a generated serial with a typed one (unit edit modal → `ProductUnitCorrectionSerializer`, `ProductUnitSerializer` PUT/PATCH, or Django admin), the flag flips to False: it is now a real serial. This is done in the serializers/admin (after the unchanged service call, in one atomic block), not in `services.py`. The serial change is already audit-logged by the existing `RecordChange`.

### D2. Data migration

`0044_productunit_serial_is_generated` (schema) followed by a data step in the same migration file (`RunPython` with a reverse), matching **in Python**, no DB regex:

A unit is marked True only if `serial == f"{product.sku}-{rest}"` and `rest` is exactly one of:

- Receiving format: `\d{6}-\d{2,}-\d{3,}` (batch, line, serial index; `padStart` minimums)
- Add Unit format: `\d{6}-\d{3,}`

using the unit's **own product's SKU as the prefix**. Anything else is left False. The migration prints (and the implementation report records) the number matched and a list of **near-misses**: units whose serial ends in a generated-looking suffix (`-dddddd-dd-ddd` / `-dddddd-ddd`) or starts with their SKU but did not match exactly. Near-misses are listed, never guessed. Reverse is a no-op for data (the column is dropped by the schema step's reverse). The matching function is duplicated inside the migration (migrations must not import app code that can change).

Dev DB result: see the report (surveyed before the change: 142 units, 64 matching, 0 near-misses).

### D3. Pickers (Delivery, Reservation, Issue, Repair, Removal; Client Return in D4)

All six share one pattern, so they share one set of helpers in `AppRouter.jsx` (kept in the single file):

- `buildUnitPickerRows(units, selectedIds, query)`: real units stay one row each exactly as today; generic units of the same product **and status** merge into one row. Search text for a generic row is the product fields only (a generated serial is not a thing a person searches). The existing 8-row cap applies to rows after grouping.
- `GenericUnitRow`: product, SKU, "No serial · N available" (label follows the unit status: "N available" in available-only pickers, e.g. "N reserved" in Removal), a quantity input (default 1, clamped to 1..N), an Add button (Enter also adds).
- `oldestGenericUnits(units, n)`: sorts by `purchase_date` (the receiving/entry date), nulls last, then `id`, and takes `n`.
- Selected list: generic units of one product+status show as one row ("N units · no serial") with one remove button; real units stay one row each. Mixed selections are allowed. Delivery's per-unit reference sale price is one input per generic row, applied to each unit in it.
- Scanning an exact serial (generated or real) still selects that single unit.
- Submitted payloads are unchanged (`unit_ids`, `unit_sale_prices`).

**Taken-unit error.** If a picked unit was changed by someone else meanwhile, the existing service validation raises `ValidationError`, the serializers already convert it to a 400 and the page shows it through `firstApiError`. Tests assert a 400 with a readable message (not a 500) for each of the six endpoints.

### D4. Client Return

Feasible cleanly with existing data, so it is **not** left manual:

- Client Return's pool is `returnable_units` (sold units, client derived from the unit's latest completed delivery). That list is limited and server-searched, so generic units are served separately: a new read-only endpoint `GET client-returns/returnable-generic-groups/` (`q`, `delivery` params, same `VIEW_CLIENT_RETURN_RECORD` permission) returns one group per (product, client): `count` and `unit_ids` ordered **oldest delivery first** (`delivery_date`, then delivery item id).
- Eligibility mirrors `create_client_return_record` exactly: active, `sold`, has a latest completed delivery item, not already returned under that item, delivery has a client, and (when `delivery` is given) is from that delivery. A test proves the ids the endpoint hands out are accepted by the real service.
- `returnable_units` no longer lists generic units in its default individual list (they would crowd out real units under its limit), except when `q` equals a generated serial exactly (so scanning still selects that unit).
- The page's existing rule stays: the return's client comes from the first selected unit, and afterwards only that client's rows are offered, generic groups included. Group rows show the client name and the quantity picked takes the oldest deliveries first.

### D5. Display (record detail pages)

Item serializers (`Receiving/Delivery/Reservation/Issue/Repair/Removal/ClientReturnItemSerializer`) expose `serial_is_generated`. A shared `groupGenericItems(items)` helper merges generic items of one product that look identical (same product, unit status, active flag, notes and price/cost) into one line with a count and "no serial"; real serials are listed individually. Applied to the seven item tables and to the two edit panels that list items (Receiving: cost/notes, Delivery: notes; editing a merged line applies to every item in it). `Unit #id` lines show the count for a merged line.

Stock Units view: still every unit with its serial; adds a "Serial" column (Generated / Real). CSV export gains a `Serial Type` column (`Generated`/`Real`) after `Serial Number`. The Product Details unit register shows the same Generated tag beside the serial (same data, same pattern).

### D6. Sync (convention 5) and tests that read the source

No new status or module, so `ui_config.py` / `uiRegistry.js` need no new tokens. The "Generated"/"Real" labels live in one frontend constant. `tests.py` has a source assertion on `serial_numbers: buildReceivingSerialNumbers(line, lineIndex)` (receiving submit); it is updated deliberately because generation moves to the backend. Other source assertions are checked by running the suite; function ordering in `AppRouter.jsx` that tests slice on (e.g. `StockEntryPage` → `CreateDeliveryPage`) is preserved.

## Approaches considered

1. **Frontend-only flag** (frontend marks the units it generated). Smallest, but the flag can drift from the serial and any API client could mark real serials as generic. Rejected.
2. **Edit `create_receiving_record` to generate and flag.** Cleanest at the data layer but violates "do not change the stock services". Rejected.
3. **Chosen:** generate in the serializer layer in `serials.py`, flag in the same transaction, services untouched.

For quantity resolution: resolving on the backend (an "N of product P" payload) would need service changes; resolving to unit ids in the frontend keeps services untouched. Chosen.

## Risks

- `AppRouter.jsx` is large; helper placement must not break the source-slicing tests.
- Client Return group endpoint duplicates eligibility logic from the service; mitigated by the acceptance test above.
- Existing real data: old generic units flagged only by exact match. Units with generated-looking serials on a renamed product (SKU changed after receiving) show up as near-misses and stay "real" until someone decides.

## Acceptance

See the verification list in the plan: migration created and applied to the dev DB; `check`; `makemigrations --check`; focused tests (flag on every creation path, migration matching, oldest-first, client-return restriction, taken-unit error, services/StockMovement untouched); `npm run build`; `git diff --check`; full suite.
