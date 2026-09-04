a
- `role_id` (INTEGER, FK -> `roles.id`, NOT NULL)
- `status` (VARCHAR(20), DEFAULT `'active'`) — `'active'`, `'inactive'`
- `created_at`, `updated_at` (DATETIME)

#### `password_reset_tokens`
Tokens for user password recovery flows.
- `id` (INTEGER, PK)
- `user_id` (INTEGER, FK -> `users.id`, NOT NULL)
- `token` (VARCHAR(100), UNIQUE, NOT NULL)
- `expires_at` (DATETIME, NOT NULL)
- `is_used` (BOOLEAN, DEFAULT `False`)

---

### 3.2 Product Catalog & Inventory

#### `categories`
Product classification categories.
- `id` (VARCHAR(36), PK, UUID)
- `category_code` (VARCHAR(20), UNIQUE, NOT NULL, INDEX)
- `name` (VARCHAR(100), NOT NULL)
- `description` (TEXT)
- `status` (VARCHAR(20), DEFAULT `'active'`)
- `created_at`, `updated_at` (DATETIME)

#### `brands`
Product brands/manufacturers.
- `id` (VARCHAR(36), PK, UUID)
- `brand_name` (VARCHAR(100), NOT NULL, UNIQUE)
- `description` (TEXT)
- `status` (VARCHAR(20), DEFAULT `'active'`)
- `created_at`, `updated_at` (DATETIME)

#### `products`
Master inventory items.
- `id` (VARCHAR(36), PK, UUID)
- `product_code` (VARCHAR(50), UNIQUE, NOT NULL, INDEX)
- `barcode` (VARCHAR(100), UNIQUE, INDEX)
- `qr_code` (VARCHAR(100), NULLABLE)
- `product_name` (VARCHAR(150), NOT NULL)
- `category_id` (VARCHAR(36), FK -> `categories.id`, NOT NULL)
- `brand_id` (VARCHAR(36), FK -> `brands.id`, NULLABLE)
- `purchase_price` (NUMERIC(10,2), NOT NULL)
- `selling_price` (NUMERIC(10,2), NOT NULL)
- `gst_percentage` (NUMERIC(5,2), DEFAULT `18.00`)
- `discount_percentage` (NUMERIC(5,2), DEFAULT `0.00`)
- `current_stock` (INTEGER, DEFAULT `0`, NOT NULL)
- `minimum_stock` (INTEGER, DEFAULT `5`)
- `maximum_stock` (INTEGER, DEFAULT `500`)
- `unit` (VARCHAR(20), DEFAULT `'pcs'`)
- `status` (VARCHAR(20), DEFAULT `'active'`)
- `created_at`, `updated_at` (DATETIME)

#### `inventory_movements`
Audit log of stock entries (Stock In / Stock Out / Adjustments).
- `id` (VARCHAR(36), PK, UUID)
- `product_id` (VARCHAR(36), FK -> `products.id`, NOT NULL)
- `movement_type` (VARCHAR(50), NOT NULL) — `'Stock In'`, `'Stock Out'`, `'Sale Checkout'`, `'Adjustment'`
- `quantity` (INTEGER, NOT NULL)
- `previous_stock` (INTEGER, NOT NULL)
- `new_stock` (INTEGER, NOT NULL)
- `remarks` (TEXT)
- `created_by` (INTEGER, FK -> `users.id`)
- `created_at` (DATETIME)

---

### 3.3 Customer Accounts

#### `customers`
Customer demographic and credit accounts profile.
- `id` (VARCHAR(36), PK, UUID)
- `customer_code` (VARCHAR(20), UNIQUE, NOT NULL, INDEX)
- `first_name` (VARCHAR(50), NOT NULL)
- `last_name` (VARCHAR(50), NOT NULL)
- `full_name` (VARCHAR(100), NOT NULL)
- `phone_number` (VARCHAR(20), UNIQUE, NOT NULL, INDEX)
- `alternate_phone` (VARCHAR(20))
- `email` (VARCHAR(120), UNIQUE, INDEX)
- `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`
- `date_of_birth` (DATE, NOT NULL)
- `gender` (VARCHAR(15), NOT NULL)
- `occupation` (VARCHAR(50))
- `aadhaar_number` (VARCHAR(20))
- `status` (VARCHAR(20), DEFAULT `'active'`)
- `created_at`, `updated_at` (DATETIME)
- `deleted_at` (DATETIME) — *Soft deletion flag*

#### `customer_ledger`
Running debit/credit statement ledger.
- `id` (VARCHAR(36), PK, UUID)
- `customer_id` (VARCHAR(36), FK -> `customers.id`, NOT NULL)
- `transaction_type` (VARCHAR(20), NOT NULL) — `'debit'` (invoice sale), `'credit'` (payment receipt)
- `reference_id` (VARCHAR(36), NOT NULL)
- `description` (TEXT, NOT NULL)
- `debit` (NUMERIC(10,2), DEFAULT `0.00`)
- `credit` (NUMERIC(10,2), DEFAULT `0.00`)
- `balance` (NUMERIC(10,2), NOT NULL) — *Running balance*
- `transaction_date` (DATETIME, NOT NULL)
- `created_at` (DATETIME)

---

### 3.4 POS Sales & Instalment Plans

#### `sales`
POS Checkout invoices.
- `id` (VARCHAR(36), PK, UUID)
- `invoice_number` (VARCHAR(50), UNIQUE, NOT NULL, INDEX)
- `customer_id` (VARCHAR(36), FK -> `customers.id`, NOT NULL)
- `sale_date` (DATETIME, NOT NULL, INDEX)
- `subtotal` (NUMERIC(10,2), NOT NULL)
- `discount_amount` (NUMERIC(10,2), DEFAULT `0.00`)
- `tax_amount` (NUMERIC(10,2), DEFAULT `0.00`)
- `grand_total` (NUMERIC(10,2), NOT NULL)
- `down_payment` (NUMERIC(10,2), DEFAULT `0.00`)
- `remaining_balance` (NUMERIC(10,2), DEFAULT `0.00`)
- `payment_status` (VARCHAR(20), DEFAULT `'pending'`) — `'paid'`, `'partial'`, `'pending'`
- `sale_status` (VARCHAR(20), DEFAULT `'completed'`) — `'completed'`, `'cancelled'`
- `created_at`, `updated_at` (DATETIME)

#### `sale_items`
Individual items sold in a POS invoice.
- `id` (VARCHAR(36), PK, UUID)
- `sale_id` (VARCHAR(36), FK -> `sales.id`, NOT NULL)
- `product_id` (VARCHAR(36), FK -> `products.id`, NOT NULL)
- `quantity` (INTEGER, NOT NULL)
- `unit_price` (NUMERIC(10,2), NOT NULL)
- `discount` (NUMERIC(10,2), DEFAULT `0.00`)
- `tax` (NUMERIC(5,2), DEFAULT `0.00`)
- `total_price` (NUMERIC(10,2), NOT NULL)

#### `instalment_plans`
Credit instalment contract agreements.
- `id` (VARCHAR(36), PK, UUID)
- `plan_number` (VARCHAR(50), UNIQUE, NOT NULL, INDEX)
- `sale_id` (VARCHAR(36), FK -> `sales.id`, NOT NULL)
- `customer_id` (VARCHAR(36), FK -> `customers.id`, NOT NULL)
- `invoice_number` (VARCHAR(50), NOT NULL)
- `total_amount` (NUMERIC(10,2), NOT NULL)
- `down_payment` (NUMERIC(10,2), NOT NULL)
- `remaining_balance` (NUMERIC(10,2), NOT NULL)
- `number_of_instalments` (INTEGER, NOT NULL)
- `monthly_emi` (NUMERIC(10,2), NOT NULL)
- `interest_rate` (NUMERIC(5,2), DEFAULT `0.00`)
- `processing_fee` (NUMERIC(10,2), DEFAULT `0.00`)
- `start_date` (DATETIME, NOT NULL)
- `first_due_date` (DATETIME, NOT NULL)
- `last_due_date` (DATETIME, NOT NULL)
- `status` (VARCHAR(20), DEFAULT `'active'`) — `'active'`, `'completed'`, `'overdue'`, `'cancelled'`
- `created_at`, `updated_at` (DATETIME)

#### `instalment_schedules`
Monthly EMI due breakdown lines.
- `id` (VARCHAR(36), PK, UUID)
- `plan_id` (VARCHAR(36), FK -> `instalment_plans.id`, NOT NULL)
- `instalment_number` (INTEGER, NOT NULL)
- `due_date` (DATETIME, NOT NULL, INDEX)
- `amount` (NUMERIC(10,2), NOT NULL)
- `paid_amount` (NUMERIC(10,2), DEFAULT `0.00`)
- `balance` (NUMERIC(10,2), NOT NULL)
- `paid_date` (DATETIME, NULLABLE)
- `days_overdue` (INTEGER, DEFAULT `0`)
- `payment_status` (VARCHAR(20), DEFAULT `'pending'`) — `'pending'`, `'paid'`, `'partially_paid'`, `'overdue'`
- `remarks` (TEXT)

---

### 3.5 Payments & Receipts

#### `payments`
Collections and cash receipts.
- `id` (VARCHAR(36), PK, UUID)
- `receipt_number` (VARCHAR(50), UNIQUE, NOT NULL, INDEX)
- `plan_id` (VARCHAR(36), FK -> `instalment_plans.id`, NULLABLE)
- `schedule_id` (VARCHAR(36), FK -> `instalment_schedules.id`, NULLABLE)
- `sale_id` (VARCHAR(36), FK -> `sales.id`, NULLABLE)
- `invoice_number` (VARCHAR(50), NULLABLE)
- `customer_id` (VARCHAR(36), FK -> `customers.id`, NOT NULL)
- `payment_date` (DATETIME, NOT NULL, INDEX)
- `payment_amount` (NUMERIC(10,2), NOT NULL)
- `payment_type` (VARCHAR(50), NOT NULL) — `'EMI Payment'`, `'Direct Payment'`, `'Adjustment Payment'`
- `payment_method` (VARCHAR(50), NOT NULL) — `'Cash'`, `'UPI'`, `'Credit Card'`, `'Debit Card'`, `'Bank Transfer'`, `'Cheque'`
- `reference_number` (VARCHAR(100), NULLABLE)
- `bank_name` (VARCHAR(100), NULLABLE)
- `transaction_id` (VARCHAR(100), NULLABLE)
- `remarks` (TEXT)
- `received_by` (INTEGER, FK -> `users.id`, NULLABLE)
- `payment_status` (VARCHAR(20), DEFAULT `'paid'`) — `'paid'`, `'refunded'`
- `created_at`, `updated_at` (DATETIME)

#### `payment_receipts`
Printable receipt descriptors.
- `id` (VARCHAR(36), PK, UUID)
- `receipt_number` (VARCHAR(50), UNIQUE, NOT NULL, INDEX)
- `payment_id` (VARCHAR(36), FK -> `payments.id`, NOT NULL)
- `invoice_number` (VARCHAR(50), NULLABLE)
- `customer_id` (VARCHAR(36), FK -> `customers.id`, NOT NULL)
- `receipt_date` (DATETIME, NOT NULL, INDEX)
- `amount_received` (NUMERIC(10,2), NOT NULL)
- `payment_method` (VARCHAR(50), NOT NULL)
- `generated_by` (INTEGER, FK -> `users.id`)

---

### 3.6 System Audit & Settings

#### `audit_logs`
Activity tracking log.
- `id` (INTEGER, PK, Auto-increment)
- `user_id` (INTEGER, FK -> `users.id`, NULLABLE)
- `username` (VARCHAR(50), NOT NULL)
- `action` (VARCHAR(255), NOT NULL)
- `ip_address` (VARCHAR(45))
- `user_agent` (VARCHAR(255))
- `timestamp` (DATETIME, DEFAULT `utcnow()`)

#### `settings`
Global shop configuration key-value store.
- `id` (INTEGER, PK, Auto-increment)
- `key` (VARCHAR(50), UNIQUE, NOT NULL, INDEX)
- `value` (TEXT, NOT NULL)
- `updated_at` (DATETIME)

---

## 4. How to Set Up & Initialize the Database

### Method A: Out-of-the-Box SQLite Initialization
The database initializes automatically when starting `app.py`.

```powershell
# 1. Activate Virtual Environment
.\venv\Scripts\activate

# 2. Run Flask App (creates instance/instalment_shop.db and seeds initial data)
python app.py
```

### Method B: Manual Python Initialization / Reseed

```powershell
# Run seeder script inside python shell
$env:PYTHONPATH="c:\Instalmentshopmanage"
.\venv\Scripts\python.exe -c "from app import create_app; from database import init_db; app = create_app(); init_db(app)"
```

### Method C: PostgreSQL / Supabase Setup
To use PostgreSQL instead of SQLite, update `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/payease_db
SECRET_KEY=your-custom-secret-key
```

Then run `python app.py` to auto-create all tables and seed default roles and admin accounts.
