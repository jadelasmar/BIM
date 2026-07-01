# Database

Local development uses SQLite:

```text
db.sqlite3
```

Django settings point to the root database file from `backend/bim/settings.py`.

## Stock Models

### Category

Groups products into a product family.

Fields:

- `name`

### Brand

Stores manufacturer or brand names.

Fields:

- `brandname` unique

### ProductModel

Stores a model under a brand.

Fields:

- `brand`
- `modelname`

Constraint:

- unique `(brand, modelname)`

### Product

Product definition. This is not a physical stock unit.

Fields:

- `descript`
- `category`
- `model`
- `sku`
- `barcode`
- `image`
- `reorder_stock_level`
- `crdate`
- `isactive`

Rules:

- SKU is auto-generated from category, brand, and model.
- Product quantity is calculated from active `ProductUnit` rows.
- Soft delete uses `isactive`.
- Current image upload path is `products_images/`.

### Supplier

Stores companies or people stock is bought from.

Fields:

- `name` unique

### ProductUnit

One physical stock item.

Fields:

- `product`
- `serial_number`
- `status`
- `supplier`
- `cost`
- `selling_price`
- `purchase_date`
- `sold_date`
- `notes`
- `crdate`
- `isactive`

Statuses:

- `available`
- `reserved`
- `sold`
- `returned`
- `inactive`

When a unit is saved as sold, `sold_date` is filled if empty.

### ReceivingRecord

Operational inbound receiving record. This is not a supplier invoice or accounting document.

Fields:

- `receiving_number`
- `supplier`
- `reference_number`
- `received_date`
- `notes`
- `created_by`
- `crdate`
- `isactive`

Rules:

- Supplier is optional for direct/manual receiving.
- Reference number stores an optional supplier document/reference.
- Receiving numbers are generated as `RCV-YYYY-0001`.

### ReceivingItem

Line item for a receiving record.

Fields:

- `receiving`
- `product`
- `product_unit`
- `quantity`
- `serial_number`
- `cost`
- `notes`
- `crdate`
- `isactive`

Rules:

- `quantity` supports non-serialized receiving.
- Serialized receiving creates one item per serial number and links each item to a `ProductUnit`.
- `cost` is operational/reference cost only; it does not create accounting, invoice, tax, payment, or voucher behavior.

### DeliveryRecord

Outbound delivery record.

Fields:

- `delivery_number`
- `customer_name`
- `receiver_name`
- `delivery_date`
- `notes`
- `status`
- `created_by`
- `crdate`
- `isactive`

Rules:

- Delivery numbers are generated as `DLV-YYYY-0001`.
- Current default status is completed.

### DeliveryItem

Connects delivered stock units to a delivery record.

Fields:

- `delivery`
- `product_unit`
- `product`
- `notes`
- `crdate`
- `isactive`

Rules:

- `product_unit` is one-to-one to prevent one physical unit from being delivered more than once.

## Migration Strategy

- Preserve existing migrations.
- Do not rename app labels.
- Avoid unnecessary migrations.
- Keep `bim_stock` and `bim_accounts` labels for compatibility.
- Add new models only when the workflow needs durable data.

## Future Data Expansion

Likely future models:

- `StockMovement`
- attachments/documents
- clients
- assets
- audit logs
