# PayEase - UML Class Diagram

This document contains the detailed UML Class Diagram for the **PayEase - Instalment Shop Management System**, representing the system's data model, class attributes, data types, class methods, and entity relationships.

The diagram is written in **Mermaid.js** syntax and renders dynamically.

---

## Class Diagram

```mermaid
classDiagram
    direction TB

    class Role {
        +int id
        +str role_name
        +str description
    }

    class User {
        +int id
        +str username
        +str email
        +str password_hash
        +int role_id
        +str status
        +set_password(password: str) void
        +check_password(password: str) bool
    }

    class PasswordResetToken {
        +int id
        +int user_id
        +str token_hash
        +datetime created_at
        +datetime expires_at
        +datetime used_at
        +generate_token_pair(user_id: int, lifetime_minutes: int) tuple$
        +verify_token(raw_token: str) PasswordResetToken$
        +mark_as_used() void
    }

    class AuditLog {
        +int id
        +int user_id
        +str username
        +str action
        +str ip_address
        +str user_agent
        +datetime timestamp
        +log(action: str, user_id: int, username: str) void$
    }

    class Category {
        +str id
        +str category_code
        +str name
        +str description
        +str status
    }

    class Brand {
        +str id
        +str brand_name
        +str description
        +str status
    }

    class Product {
        +str id
        +str product_code
        +str barcode
        +str qr_code
        +str product_name
        +str category_id
        +str brand_id
        +str description
        +Decimal purchase_price
        +Decimal selling_price
        +Decimal gst_percentage
        +int current_stock
        +int minimum_stock
        +int maximum_stock
        +str unit
        +str status
    }

    class InventoryMovement {
        +str id
        +str product_id
        +str movement_type
        +int quantity
        +int previous_stock
        +int new_stock
        +str remarks
        +int created_by
        +datetime created_at
    }

    class Customer {
        +str id
        +str customer_code
        +str first_name
        +str last_name
        +str full_name
        +str email
        +str phone_number
        +str address_line1
        +str city
        +str state
        +str postal_code
        +str country
        +date date_of_birth
        +str gender
        +str status
        +float outstanding_balance
    }

    class Sale {
        +str id
        +str invoice_number
        +str customer_id
        +datetime sale_date
        +Decimal subtotal
        +Decimal discount_amount
        +Decimal tax_amount
        +Decimal grand_total
        +Decimal down_payment
        +Decimal remaining_balance
        +str payment_status
        +str sale_status
        +int created_by
    }

    class SaleItem {
        +str id
        +str sale_id
        +str product_id
        +int quantity
        +Decimal unit_price
        +Decimal discount
        +Decimal tax
        +Decimal total_price
    }

    class InstalmentPlan {
        +str id
        +str plan_number
        +str sale_id
        +str customer_id
        +str invoice_number
        +Decimal total_amount
        +Decimal down_payment
        +Decimal remaining_balance
        +int number_of_instalments
        +Decimal monthly_emi
        +Decimal interest_rate
        +Decimal processing_fee
        +datetime start_date
        +datetime first_due_date
        +datetime last_due_date
        +str status
        +Decimal paid_amount
        +Decimal outstanding_amount
        +int completed_count
    }

    class InstalmentSchedule {
        +str id
        +str plan_id
        +int instalment_number
        +date due_date
        +Decimal amount
        +Decimal paid_amount
        +Decimal balance
        +str payment_status
        +datetime paid_date
        +int days_overdue
        +str remarks
    }

    class Payment {
        +str id
        +str receipt_number
        +str plan_id
        +str schedule_id
        +str sale_id
        +str invoice_number
        +str customer_id
        +datetime payment_date
        +float payment_amount
        +str payment_type
        +str payment_method
        +str reference_number
        +str bank_name
        +str transaction_id
        +str remarks
        +int received_by
        +str payment_status
    }

    class PaymentReceipt {
        +str id
        +str receipt_number
        +str payment_id
        +str invoice_number
        +str customer_id
        +datetime receipt_date
        +Decimal amount_received
        +str payment_method
        +int generated_by
    }

    class CustomerLedger {
        +str id
        +str customer_id
        +str transaction_type
        +str reference_id
        +str description
        +Decimal debit
        +Decimal credit
        +Decimal balance
        +datetime transaction_date
    }

    class Setting {
        +str key
        +str value
        +get_val(key: str, default: str) str$
        +set_val(key: str, value: str) void$
    }

    %% Relationships
    Role "1" -- "0..*" User : assigns
    User "1" -- "0..*" AuditLog : logs
    User "1" -- "0..*" PasswordResetToken : requests
    Category "1" -- "0..*" Product : groups
    Brand "1" -- "0..*" Product : manufactures
    Product "1" -- "0..*" SaleItem : lists
    Product "1" -- "0..*" InventoryMovement : adjusts
    Customer "1" -- "0..*" Sale : checkouts
    Customer "1" -- "0..*" InstalmentPlan : pays
    Customer "1" -- "0..*" CustomerLedger : bills
    Sale "1" -- "0..*" SaleItem : contains
    Sale "1" -- "0..1" InstalmentPlan : triggers
    InstalmentPlan "1" -- "0..*" InstalmentSchedule : breaks
    InstalmentPlan "1" -- "0..*" Payment : collects
    InstalmentSchedule "1" -- "0..*" Payment : bills
    Payment "1" -- "1" PaymentReceipt : copies
```

---

## Entity Descriptions

### 1. User Authentication & Roles
* **`Role`**: Maps user permission privileges (Super Admin, Admin, Staff).
* **`User`**: System operators with email, hashed passwords, and active account flags.
* **`PasswordResetToken`**: Cryptographic SHA-256 tokens allowing secure, timed password resets.
* **`AuditLog`**: Centralized actions trail capturing client IP addresses and transaction summaries.

### 2. Product Catalog & Inventory
* **`Category`**: Grouping products (e.g. Electronics, Furniture).
* **`Brand`**: Brands manufacturing the products.
* **`Product`**: Stockable catalog items with purchase/selling price lists and low stock limits.
* **`InventoryMovement`**: Historical ledger tracking stock adjustments (Stock In / Stock Out).

### 3. POS Sales & Instalment Plans
* **`Customer`**: Client details tracking overall outstanding balances.
* **`Sale`**: Aggregate transaction details recording subtotal, tax amounts, and down payments.
* **`SaleItem`**: Individual checkout cart items listing prices, quantities, and GST.
* **`InstalmentPlan`**: Active instalment payment plans mapping down payments, monthly EMI values, and interest.
* **`InstalmentSchedule`**: Monthly schedule rows tracking specific due dates, paid values, and overdue counts.
* **`Payment`**: Collection transactions recording cash/UPI transfers mapping receipt references.
* **`PaymentReceipt`**: Legally compliant physical receipt references.
* **`CustomerLedger`**: Double-entry ledger ledger columns mapping debits (sales) and credits (collection payments) sequentially.
* **`Setting`**: Key-value pairs configuration settings.
