# User Manual

This manual guides cashiers and managers on how to navigate the Instalment Shop Management System daily.

---

## 🔐 System Log In
1. Open the application URL in your browser.
2. Enter your assigned username/email and password.
3. Click **Sign In**.

---

## 📊 Dashboard Overview
The central dashboard displays real-time KPI metrics:
* **Active Dues**: Combined unpaid customer balance.
* **Low Stock Alerts**: Count of products whose stock is below minimum levels.
* **Overdue Instalments**: Unpaid EMIs whose due dates have passed.

---

## 👥 Customer Profile Management
To register a new customer:
1. Navigate to **Customers** in the sidebar.
2. Click **Add Customer** in the top right.
3. Populate the first name, last name, phone number, and address fields.
4. Click **Create Customer**.
5. Once created, click on their profile link to view their **Ledger Statement** containing full purchase/payment history.

---

## 📦 Products & Stock Control
To review inventory levels:
1. Click **Products** in the sidebar to view the active catalog.
2. Under **Inventory**, view the current opening and closing stock records.
3. Low-stock products will show a yellow warning badge (`LOW STOCK`).

---

## 🧾 Point of Sale (POS) & Billing Checkout
To checkout a customer purchase:
1. Click **POS Terminal** in the sidebar.
2. Select the customer from the dropdown.
3. Search and select products to add to the cart.
4. Enter the customer's **Down Payment** amount.
5. Select the **Instalment Months** (e.g. 3, 6, 12 months) and select the monthly **Due Day**.
6. The system calculates the monthly EMI amount automatically.
7. Click **Confirm Checkout** to complete the sale, generate the invoice, and automatically spawn the instalment schedule.

---

## 💳 Collecting Payments
To record an EMI instalment collection:
1. Navigate to **Payments & Backups** in the sidebar.
2. Click **Record Payment** (or click the green quick action in a customer's profile).
3. Search and select the customer.
4. Select the target **Instalment Plan** and select the specific unpaid instalment month.
5. Enter the cash/UPI amount received.
6. Click **Save Payment**. The system:
   * Marks the instalment month `'paid'` or `'partially_paid'`.
   * Lowers the customer outstanding balance.
   * Prints the customer receipt invoice copy.
