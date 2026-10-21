# Inventory and Operations improvements

Date: 2026-10-21. Status: approved by the user for implementation ("plan check, edit and execute").

## Problems today

**Inventory**
- Only products are listed. To find one unit by serial you search, open the product, open its Stock Units tab and search again.
- Nothing says where a unit is now: which client it was delivered to, who has it on loan, which supplier is repairing it.
- The Export button is a disabled "coming later" placeholder.
- The products table cannot be sorted.

**Operations**
- Nine identical cards with no numbers: the page never says how much work is open.
- No grouping. On a phone it is a long scroll of same-looking cards.
- The Pending page (every active reservation, assignment and repair) lost its entry point when the dashboard's Pending Actions card was replaced. Now it is only reachable from a Needs Attention row.

## Changes

### Inventory

1. **Products | Stock Units tabs.** The tab is kept in the URL (`?view=units`) so refresh and links keep it.
2. **Stock Units view.** Search (with scan) plus a status filter.
   - Table: Serial, Product, Status, **Where**, Supplier, Purchased, Edit.
   - Edit reuses `EditUnitModal`, the same form as the product page.
   - The serial links to the product page filtered to that unit (`?unit=`).
   - Up to 100 rows are shown, with a note to search when there are more.
3. **"Where" is computed by the server.** `GET /api/stock/product-units/?with_location=1` adds a `location` field per unit: `{text, href}` linking to the record.
   - reserved → "Reserved for X" (reservation)
   - issued → "With X" (temporary assignment)
   - repair → "At supplier X" / "In repair, no supplier" (repair)
   - sold → "Delivered to X" (latest completed delivery)
   - client's own item → "Belongs to X"
   - available → "In stock"
   - removed → "Removed"
   
   A new selector, `unit_locations(units)`, makes one bulk query per status (no per-row queries). Without the flag the endpoint is unchanged.
4. **Export works.** It downloads a CSV of the current view (products, or stock units with Where) as filtered. The file has a UTF-8 BOM so Excel shows Arabic names correctly. The disabled placeholder is removed.
5. **Sortable products table.** Click Product or Stock to sort; click again to reverse. The default order stays as it is now.

### Operations

6. **Open work at the top**, from the same providers as the Command Center:
   - Needs Attention rows for operations and client upgrades.
   - A "View all open work" link to the Pending page.
   
   `dashboard` is now built for `/` and `/operations/`; still not for any other page.
7. **Workflows grouped**: Stock in (Receive Stock, Add Unit), Stock out (Create Delivery, Remove Unit), Holds & loans (Reservation, Temporary Assignment), Repairs & returns (Repair, Client Return), Clients (Client Upgrade). Empty groups are hidden.
8. **Live count on each card**, e.g. "1 active", "2 received in 30 days". Counts come from the provider stats, which gain a stable `key` (`active_reservations`, `open_repairs`, ...). The cards are more compact, with a "New" button and a "Records" link; one column on a phone.
9. **Attention rows gain a `module` field** (`stock`, `operations`, `clients`) so a page can show just its own rows.

## Plan check (problems found in the first draft and how they were fixed)

1. **The tests pin the Export placeholder.** `tests.py` asserts "Export coming later" and `disabled` in `InventoryHeader`. Export now exists, so those assertions change to check the working export, as was done for the Scan placeholder.
2. **Location on every unit request would be slow.** The units endpoint is also used by every workflow picker. Location is computed only when `with_location=1` is asked for, and in bulk.
3. **Matching counts to cards by label text is fragile.** Stats get a stable `key`, and the Operations page looks counts up by key.
4. **Filtering attention rows by URL prefix is fragile.** Rows get an explicit `module` field instead.
5. **Test slices.** Some tests read slices of `AppRouter.jsx` between named functions (`InventoryTable`→`TableMessage`, `ProductDetail`→`ProductDetailsPage`). New components go where they do not break those slices' NotIn checks; `onSelect(product.id)` stays in `InventoryTable`.
6. **Same pattern elsewhere.** The unit table reuses the product page's Edit form and status badge, so editing works the same in both places.
7. **No duplicate search.** The Products view keeps its serial search; the Units view is for unit-level work.

## Out of scope

Pagination on the server, bulk edit, Excel `.xlsx` (CSV opens in Excel), and stock reports.

## Verification

`manage.py check`, `npm run build`, browser screenshots at phone and desktop width with no page errors, a check of the location API, and focused tests in `apps/stock/tests.py`. Per CLAUDE.md, the suite runs only when asked.
