# BIM Nexus Office Testing Plan

## Objective

Validate BIM Nexus core stock operations with realistic office usage before reports and secondary modules are started. The test should confirm that users can create products, receive stock, move stock through the main workflows, deliver stock, return stock from clients, and trust inventory counts and movement history.

This is an internal office test plan, not a deployment or server setup guide. Keep server setup details in `docs/Development.md`.

## Test Scope

Test these areas end to end:

- User creation
- Roles and permissions
- Login and logout
- Product creation
- Supplier creation
- Client creation
- Manual Add Unit
- Receive Stock
- Receiving edit and cancel
- Reservation create, release, and cancel
- Issue create and return
- Repair create and resolve
- Delivery create, edit, and cancel
- Client Return to available
- Client Return to repair
- Product movement history
- Dashboard counts
- Inventory filters
- Permission behavior for non-admin users

## Test Users

Create a small set of office test users:

- Admin / IT lead: can use Django admin, create users, assign groups, and perform all stock workflow tests.
- IT staff user: should be in `IT Support`; can run normal office stock workflows such as product/unit entry, receiving, reserving, issuing, repairing, delivering, client returns, and supplier/client creation.
- View-only user: should be in `Viewer`; can log in and view dashboard, inventory, suppliers, clients, records, and movement history, but should not be able to create or change stock records.

Use the existing BIM Nexus groups where possible. Keep the number of users small for the first test so permission problems are easier to trace.

## Test Data

Use a small realistic dataset:

- 2 or 3 products.
- Serialized items for each product.
- 1 supplier.
- 1 or 2 sample clients.
- Realistic serial numbers, such as `POS-TEST-001`, `POS-TEST-002`, and `PRN-TEST-001`.

Suggested products:

- POS Terminal Test Model
- Receipt Printer Test Model
- Barcode Scanner Test Model

## Step-by-Step Test Flow

1. Create users, groups, and permissions.
   Confirm the Admin / IT lead, IT staff user, and View-only user can be identified clearly.

2. Log in as admin.
   Confirm the dashboard opens and the admin can access stock workflows.

3. Create a supplier if needed.
   Use one simple supplier name for testing, such as `Office Test Supplier`.

4. Create a client.
   Use one simple client name for delivery testing, such as `Office Test Client`.

5. Create products.
   Create 2 or 3 products with names, categories, brands, models, and reorder levels.

6. Receive stock.
   Receive multiple serialized units for at least one product.

7. Confirm stock appears as available.
   Check inventory, product detail, and dashboard counts.

8. Edit receiving details.
   Update safe receiving fields such as supplier, reference, received date, notes, item cost, or item notes.

9. Cancel a test receiving record.
   Cancel only a receiving record whose units have not been used. Confirm linked units become inactive.

10. Manually add a unit.
   Use `/inventory/stock-units/new/` to add one direct stock unit. Confirm it appears as available and has movement history.

11. Reserve a unit.
    Create a reservation from an available unit. Confirm the unit becomes reserved.

12. Release or cancel reservation.
    Release one reservation and confirm the unit returns to available. If useful, create a second reservation and cancel it.

13. Issue a unit.
    Create an issue from an available unit. Confirm the unit becomes issued.

14. Return issued unit.
    Return the issue and confirm the unit becomes available again.

15. Send a unit to repair.
    Create a repair record from an available unit. Confirm the unit becomes repair.

16. Resolve repair to available.
    Resolve one repair and confirm the unit becomes available again.

17. Resolve another repair to inactive if needed.
    Send another available unit to repair, then resolve it to inactive. Confirm it no longer counts as usable stock.

18. Create delivery.
    Deliver an available unit to a sample client.

19. Confirm delivered unit becomes sold.
    Check inventory, product detail, and dashboard counts.

20. Edit delivery details.
    Update safe delivery fields such as client, receiver, delivery date, notes, or item notes.

21. Cancel one test delivery.
    Cancel only a delivery whose unit has not been changed by another workflow. Confirm the unit returns to available.

22. Create client return from sold unit to available.
    Deliver another unit, then create a Client Return with resolution `available`. Confirm the original delivery remains completed and the unit returns to available.

23. Create client return from sold unit to repair.
    Deliver another unit, then create a Client Return with resolution `repair`. Confirm the unit becomes repair.

24. Check product movement history.
    Confirm each tested product shows the expected receive, manual add, reservation, issue, repair, delivery, delivery cancel, and client return movements.

25. Check dashboard counts.
    Confirm dashboard counts match the visible inventory status totals and Supplier/Client counts.

26. Test non-admin permissions.
    Log in as the IT staff user and confirm normal stock workflows are available without Django Admin user/group management. Log in as the View-only user and confirm write actions are blocked or hidden.

## Expected Results

Login:

- Missing login identifiers and passwords show field-specific client feedback without submitting or clearing entered values.
- Password visibility toggling changes both the icon and accessible label without clearing the password.
- Failed authentication remains generic, preserves only the submitted email/username, and clears the password.
- Ask an administrator opens the configured administrator email with an account-access request populated from the login identifier.

Receive Stock:

- Creates a Receiving Record.
- Creates available stock units.
- Writes movement history.

Reservation:

- Changes stock from available to reserved.
- Release or cancel changes stock from reserved to available.
- Reserved units cannot be delivered directly.

Issue:

- Changes stock from available to issued.
- Return from issue changes stock from issued to available.
- Issued units cannot be delivered directly.

Repair:

- Changes stock from available to repair.
- Resolve repair changes stock from repair to available or inactive.
- Reserved, issued, and sold units are not sent directly to repair in this phase.

Delivery:

- Creates a Delivery Record.
- Changes stock from available to sold.
- Delivery edit changes only safe header/detail fields.

Delivery cancel:

- Changes stock from sold to available only when the delivery is still safe to cancel.
- Does not act like a client return.

Client Return:

- Changes stock from sold to available, or from sold to repair.
- Keeps the original delivery as completed.
- Does not create a permanent returned stock status.

Dashboard and inventory:

- Counts match the actual stock statuses.
- Filters work for available, reserved, issued, sold, repair, and inactive.

Product movement history:

- Shows each important stock operation.
- Uses the correct record references.

Permissions:

- Admin / IT lead can manage users and run all workflows.
- IT staff user can run normal stock workflows but cannot manage users, groups, permissions, or system settings.
- View-only user can view records but cannot create or change stock records. Direct API attempts should be rejected.

## What To Record

For every issue found, record:

- page/action
- user role
- product/serial
- expected result
- actual result
- screenshot if useful
- severity: blocker / important / polish

Use this severity guide:

- blocker: prevents daily stock use or corrupts stock status/history
- important: workflow works but is confusing, incomplete, or risky
- polish: wording, layout, or usability improvement

## Success Criteria

Testing passes if:

- stock statuses change correctly
- movement history is accurate
- permissions behave correctly
- dashboard and inventory counts are correct
- users can understand the workflow
- no blocker prevents daily stock use

## Not In This Test

These are not part of this phase:

- reports
- analytics
- assets module
- documents/attachments
- advanced supplier/client pages
- accounting, invoices, payments, tax, vouchers, refunds, or financial posting
