# Generic (no-serial) units Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, this session). Steps use checkbox (`- [ ]`) syntax.

**Goal:** Flag auto-serialled units, pick them by quantity in every unit picker, and show them grouped on detail pages.

**Architecture:** New boolean `ProductUnit.serial_is_generated`, set by the serializer layer (new `serials.py` generates the serials) in the same transaction as creation; `services.py` is untouched. Pickers share helpers inside the single `AppRouter.jsx` and resolve a quantity to unit ids before the unchanged submit. Client Return gets one read-only endpoint for generic groups.

**Tech Stack:** Django 6 / DRF / SQLite, React 19 + Vite, Tailwind 3. No new libraries.

**Spec:** `docs/superpowers/specs/2026-11-19-generic-serial-units-design.md`

## Global Constraints

- `backend/apps/stock/services.py` has a zero diff (also no `StockMovement` changes, no locking changes).
- No DB-specific regex in SQL; migration matching is done in Python; migration is reversible (SQL Anywhere friendly).
- `AppRouter.jsx` stays one file; keep the function order that `tests.py` slices on (`StockEntryPage` directly before `CreateDeliveryPage`).
- Generated serial formats stay `SKU-<6 digits>-<2 digits>-<3 digits>` (receiving) and `SKU-<6 digits>-<3 digits>` (Add Unit).
- Oldest first = `purchase_date` ascending (nulls last), then `id`. Client Return: oldest delivery first (`delivery_date`, then delivery item id).
- `serial_is_generated` is read-only in every API serializer.
- Never touch `C:\Projects\BIM-Release`, `db_prod*`, `.env`; no push, no deploy. Commit locally per task. Commit messages end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Review Focus

- A typed serial that looks generated (`SKU-123456-001`) on a new unit → stays `serial_is_generated=False` (tested in Task 2).
- Receiving with typed serials fewer than quantity and `auto_serial_count` making up the rest, and a mismatch (`typed + auto != quantity`) → 400 (Task 2).
- Editing a generated unit's serial to a typed one → flag becomes False; editing other fields leaves it True (Task 2).
- Client Return group endpoint never hands out a unit the real service would reject (already returned, no client, wrong delivery) (Task 3).
- A picked unit taken by someone else before submit → 400 with a message on all six endpoints, never 500 (Task 4).

---

### Task 1: Model field and data migration

**Files:**
- Modify: `backend/apps/stock/models.py` (`ProductUnit`, after `serial_number`)
- Create: `backend/apps/stock/migrations/0044_productunit_serial_is_generated.py`
- Test: `backend/apps/stock/tests.py` (new `GeneratedSerialMigrationTests`)

**Interfaces:**
- Produces: `ProductUnit.serial_is_generated: bool` (default False); in the migration module a function `is_generated_serial(sku: str, serial: str) -> bool` and `find_near_misses(units) -> list` used by the test via `importlib.import_module("apps.stock.migrations.0044_productunit_serial_is_generated")`.

- [ ] **Step 1: Write failing tests** `test_match_exact_receiving_format`, `test_match_exact_add_unit_format`, `test_other_product_sku_is_not_a_match` (`is_generated_serial("ABC", "XYZ-123456-001") is False`), `test_real_serial_not_matched` (`"SN12345"`, `"ABC-1"`, `"ABC-123456-1"`, `"ABC-12345-001"` all False), `test_forward_runs_and_lists_near_misses` (create units with a matching serial, a real serial, and a `OTHERSKU-123456-001` near-miss; run the forward function with `apps` = real apps; assert only the match flips and the near-miss is reported), `test_reverse_is_a_noop`.
- [ ] **Step 2: Run** `python manage.py test apps.stock.tests.GeneratedSerialMigrationTests`. Expected: FAIL (field/migration missing).
- [ ] **Step 3: Implement** the model field (`BooleanField(default=False)`), then `makemigrations bim_stock -n productunit_serial_is_generated`; add a `RunPython(forward, reverse)` after `AddField`. `forward` iterates `ProductUnit.objects.select_related("product")`, uses a precompiled `re` for the two formats on `serial[len(sku)+1:]` when `serial.startswith(sku + "-")`, bulk-updates matches via `.filter(pk__in=...).update(...)`, prints matched count and near-miss `(id, sku, serial)` lines (near miss = not matched, but serial ends in `-dddddd-dd-ddd`/`-dddddd-ddd` or starts with its SKU followed by `-`). `reverse` is `migrations.RunPython.noop`.
- [ ] **Step 4: Run** the tests. Expected: PASS.
- [ ] **Step 5: Apply to dev DB:** `python manage.py migrate`; record the printed counts for the report. Then `makemigrations --check --dry-run`.
- [ ] **Step 6: Commit** "Add ProductUnit.serial_is_generated with data migration".

### Task 2: Backend generation, flag on every creation path, API exposure

**Files:**
- Create: `backend/apps/stock/serials.py`
- Modify: `backend/apps/stock/serializers.py` (`ProductUnitSerializer`, `ProductUnitCorrectionSerializer`, `ReceivingItemInputSerializer`, `ReceivingRecordSerializer.create`, all `*ItemSerializer`s), `backend/apps/stock/admin.py` (`ProductUnitAdmin`)
- Test: `backend/apps/stock/tests.py` (new `GeneratedSerialFlagTests`)

**Interfaces:**
- Produces in `serials.py`: `generate_receiving_serials(product: Product, line_number: int, start_index: int, count: int) -> list[str]` and `generate_unit_serial(product: Product) -> str`; both return serials not present in `ProductUnit` (bump the 6-digit batch on a collision). Also `SERIAL_RECEIVING_FORMAT`/`SERIAL_UNIT_FORMAT` documented in the module docstring.
- API: `serial_is_generated` (read-only) on `ProductUnitSerializer` and on each item serializer (`source="product_unit.serial_is_generated"`, default False; `ReceivingItemSerializer` too). Receiving item input gains `auto_serial_count` (IntegerField min 0, default 0).

- [ ] **Step 1: Write failing tests:** receiving with `quantity=3, serial_numbers=["REAL-1"], auto_serial_count=2` → 3 units, `REAL-1` False, the two others True and matching the receiving format; receiving with all typed → all False; `typed+auto != quantity` → 400; typed serial `SKU-123456-001` → False; Add Unit POST without serial → generated + True, with serial → False, serial blank on PUT → 400; client sending `serial_is_generated=true` is ignored; client-owned repair intake unit False; Django-admin-style `ProductUnit.objects.create` default False; PATCH unit correction replacing a generated serial → False, editing notes only → still True; each item serializer exposes the flag; `StockMovement` rows for generated and typed receiving are the same type/status shape (`received`, `""`→`available`) and counts equal unit counts.
- [ ] **Step 2: Run** them. Expected: FAIL.
- [ ] **Step 3: Implement** `serials.py`; in `ReceivingRecordSerializer.create` (inside `transaction.atomic()`): for each item with `auto_serial_count > 0` append generated serials after the typed ones (line number = 1-based item position), call the unchanged `create_receiving_record`, then `ProductUnit.objects.filter(serial_number__in=generated).update(serial_is_generated=True)`. `ReceivingItemInputSerializer.validate` enforces `len(serial_numbers) + auto_serial_count == quantity` when `auto_serial_count > 0` (existing rule unchanged otherwise). `ProductUnitSerializer`: add read-only field; make `serial_number` not required on create only (`validate` generates via `generate_unit_serial` and records the flag on `validated_data`), drop the unique validator message only if generation made one; `update` flips the flag to False when `serial_number` changes. `ProductUnitCorrectionSerializer.update`: after the service call, in `transaction.atomic()`, flip to False when the serial changed. Admin: show `serial_is_generated` as a read-only column and list filter; `save_model` flips it to False when the serial changed on an existing unit.
- [ ] **Step 4: Run** the new tests and `apps.stock.tests` receiving/unit tests. Expected: PASS (except the source assertion handled in Task 5).
- [ ] **Step 5: Commit** "Generate serials in the backend and flag generated units".

### Task 3: Client Return generic groups

**Files:**
- Modify: `backend/apps/stock/selectors.py` (`returnable_units`, new `returnable_generic_groups`), `backend/apps/stock/api_views.py` (new `ReturnableGenericGroupsAPIView`), `backend/apps/stock/api_urls.py`
- Test: `backend/apps/stock/tests.py` (new `ReturnableGenericGroupTests`)

**Interfaces:**
- Produces: `returnable_generic_groups(query="", delivery_id=None) -> list[dict]` → `[{"product": id, "product_name", "product_sku", "client": {"id","name"}, "count": int, "unit_ids": [ids oldest delivery first]}]`; route `client-returns/returnable-generic-groups/` (name `client-return-returnable-generic-groups`), permission `VIEW_CLIENT_RETURN_RECORD`. `returnable_units` rows gain `product`, `serial_is_generated`, and the default list excludes generic units unless `query` equals the serial case-insensitively.

- [ ] **Step 1: Write failing tests:** groups by (product, client) with counts; `unit_ids` ordered by delivery date then item id (two deliveries, older first); unit already returned under its latest delivery item is excluded; delivery without client excluded; `delivery` param restricts; `q` matches product fields only, not the serial; real-serial sold units never appear in groups; `returnable_units` omits generic units by default but returns one on an exact serial `q`; **service parity:** feeding a group's first `n` `unit_ids` to `create_client_return_record` succeeds, and the units become available; viewer without the permission gets 403.
- [ ] **Step 2: Run.** Expected: FAIL.
- [ ] **Step 3: Implement** `returnable_generic_groups` with two batched queries (`DeliveryItem` active + delivery active/completed `select_related("delivery","delivery__client")` ordered by pk; `ClientReturnItem` active ordered by pk), taking the last row per unit, applying the same eligibility conditions as `create_client_return_record`, sorting units by `(delivery.delivery_date, item.pk)`, grouping by `(product_id, client_id)`, cap 50 groups. Add the view and URL.
- [ ] **Step 4: Run.** Expected: PASS.
- [ ] **Step 5: Commit** "Client Return: serve generic units as per-client groups".

### Task 4: Taken-unit and services-untouched tests

**Files:**
- Test: `backend/apps/stock/tests.py` (new `TakenUnitErrorTests`)

- [ ] **Step 1: Write tests** (these should pass without code changes; if one 500s, fix the serializer to convert the error): for delivery, reservation, issue, repair, removal, client return: create a unit (generic, flagged), take it with another workflow (or change its status), then POST the stale `unit_ids`; assert status 400 and that the response body contains a readable string (not empty). Add `test_generic_receiving_writes_same_movements_as_typed`: counts and fields of `StockMovement` rows equal between typed and generated lines.
- [ ] **Step 2: Run** `apps.stock.tests.TakenUnitErrorTests`. Expected: PASS. Fix any 500 at its source.
- [ ] **Step 3: Verify** `git diff --stat -- backend/apps/stock/services.py` is empty.
- [ ] **Step 4: Commit** "Test taken-unit errors and unchanged movements".

### Task 5: Frontend: receiving/Add Unit and shared picker helpers

**Files:**
- Modify: `frontend/src/routes/AppRouter.jsx` (`StockEntryPage`; new helpers + `GenericUnitRow` + `UnitPickerResults` placed next to `findUnitBySerial`/`SelectedUnitsTable` after `CreateReservationPage`; `SelectedUnitsTable`; the six pickers)
- Modify: `backend/apps/stock/tests.py` (the one source assertion on `buildReceivingSerialNumbers`)
- Test: `backend/apps/stock/tests.py` (new `GenericUnitPickerSourceTests`: asserts the helpers exist, every one of the six pages uses `UnitPickerResults`/`buildUnitPickerRows`, `serial_numbers: typedSerials`, `auto_serial_count`, no `buildGeneratedSerial` remains)

**Interfaces:**
- Produces: `buildUnitPickerRows(units, selectedIds, query, { limit = 8, requireQuery = true })` → rows `{kind:"unit", unit}` | `{kind:"generic", key, product, product_name, product_sku, status, status_label, client?, units}`; `oldestGenericUnits(units, count)`; `<UnitPickerResults rows renderUnit onAddUnit onAddGenerics className />`; `SelectedUnitsTable({ units, onRemove, emptyText })` (generic units merged per product+status, remove drops every id in the row).

- [ ] **Step 1: Write the source tests** above. **Step 2: Run:** FAIL.
- [ ] **Step 3: Implement StockEntryPage:** receiving sends `serial_numbers: typedSerials` (parsed) and `auto_serial_count: quantity - typedSerials.length` (still error when typed > quantity); Add Unit POSTs omit `serial_number` when none typed for that index; remove `buildGeneratedSerial`/`serialBatch`; placeholder text "One per line. Blank = no serial (generic unit)".
- [ ] **Step 4: Implement helpers and wire** Reservation, Issue, Repair, Removal, Delivery (selected list keeps its sale-price input: one input per merged row applied to each unit id) and Client Return (loads groups from the new endpoint, builds generic rows from them; `returnClient` rule applies to groups). Reservation-derived delivery rows carry `product`, `serial_is_generated`, `status`.
- [ ] **Step 5: Run** `npm run build` (from `frontend/`) and the source tests. Expected: PASS.
- [ ] **Step 6: Commit** "Pickers: pick generic units by quantity, oldest first".

### Task 6: Frontend: grouped detail display, Stock Units column, CSV

**Files:**
- Modify: `frontend/src/routes/AppRouter.jsx` (`groupGenericItems`; `ReceivingItemsTable`, `DeliveryItemsTable`, `ReservationItemsTable`, `IssueItemsTable`, `RepairItemsTable`, `RemovalItemsTable`, `ClientReturnItemsTable`; the Receiving and Delivery edit panels; `InventoryUnitsView`; `ProductUnitRegister`; `exportCurrentView` units branch)
- Test: `backend/apps/stock/tests.py` (`GenericDisplaySourceTests`: all seven tables call `groupGenericItems`; CSV header contains `"Serial Type"`; Stock Units header contains "Serial")

**Interfaces:** `groupGenericItems(items) -> [{ key, items, count, generic }]` merging generic items with identical `product`, `product_unit_status`, `isactive`, `notes`, `sale_price`/`cost`.

- [ ] **Step 1: Write the source tests. Step 2: Run:** FAIL.
- [ ] **Step 3: Implement** the helper and the tables (merged line shows "N units" and "No serial"; real serial lines unchanged), the edit panels (merged line applies the edit to every id), the Stock Units "Serial" column (Generated/Real label constant, mobile list shows the tag), register tag, CSV `Serial Type` after `Serial Number`.
- [ ] **Step 4: Run** `npm run build` and the tests. Expected: PASS.
- [ ] **Step 5: Commit** "Group generic units on record pages; show generated vs real serials".

### Task 7: Docs and final verification

**Files:** `docs/Database.md`, `docs/Backend.md`, `docs/Frontend.md`, `docs/CodeMap.md`, `docs/Roadmap.md` (only if it lists this), `CLAUDE.md` (domain model note: `serial_is_generated`; AppRouter size is stale, leave).

- [ ] **Step 1: Update docs:** Database (field, migration rule, generated formats), Backend (serials module, `auto_serial_count`, groups endpoint, serializer flag-flip), Frontend (picker behaviour, grouped display, CSV column, receive/add-unit payload), CodeMap (new file/endpoint/flow).
- [ ] **Step 2: Run:** `python manage.py check`; `python manage.py makemigrations --check --dry-run`; `npm run build`; `git diff --check`; full `python manage.py test`. Expected: all pass.
- [ ] **Step 3: Verify** `git diff main --stat -- backend/apps/stock/services.py` is empty; `git status` shows no `backend/static/frontend/` edits staged by hand.
- [ ] **Step 4: Commit** "Docs: generic serial units".
