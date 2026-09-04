# API Documentation

This document describes the REST API endpoints provided by the Instalment Shop Management System.

---

## 🔒 Authentication Flow
All requests require a valid session cookie. Log in first using:
* **Endpoint**: `POST /auth/login`
* **Content-Type**: `application/x-www-form-urlencoded` or `multipart/form-data`
* **Form Parameters**:
  * `email_or_username`: Username or email address
  * `password`: Password string

---

## 📋 Customers API

### 1. Get Customers List
* **Endpoint**: `GET /api/customers`
* **Method**: `GET`
* **Response Example (200 OK)**:
```json
[
  {
    "id": "e45851d9-29bf-45bf-85d8-912c3ba71891",
    "customer_code": "CUST0001",
    "full_name": "Pranav Kumar",
    "email": "pranav@gmail.com",
    "phone_number": "+919876543201",
    "outstanding_balance": 43266.67,
    "status": "active"
  }
]
```

### 2. Create Customer
* **Endpoint**: `POST /api/customers`
* **Content-Type**: `application/json`
* **Request Payload**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone_number": "+919999911111",
  "address_line1": "456 Park Avenue",
  "city": "Bangalore",
  "state": "Karnataka",
  "postal_code": "560001",
  "date_of_birth": "1990-05-15",
  "gender": "Male"
}
```

---

## 📦 Products API

### 1. Create Product
* **Endpoint**: `POST /api/products`
* **Content-Type**: `application/json`
* **Request Payload**:
```json
{
  "barcode": "SKU-PROD-99",
  "product_name": "Dell Monitor 27 inch",
  "category_id": "smartphones-uuid",
  "brand_id": "dell-uuid",
  "purchase_price": 12000.00,
  "selling_price": 15000.00,
  "gst_percentage": 18.0,
  "current_stock": 25,
  "minimum_stock": 5,
  "maximum_stock": 100,
  "unit": "pcs"
}
```

---

## 🧾 Sales & Billing API

### 1. POS Checkout Invoice
* **Endpoint**: `POST /api/sales`
* **Content-Type**: `application/json`
* **Request Payload**:
```json
{
  "customer_id": "customer-uuid-string",
  "cart": [
    {
      "product_id": "product-uuid-string",
      "quantity": 1,
      "discount": 0.0
    }
  ],
  "down_payment": 5000.00,
  "total_instalments": 6,
  "due_day": 10
}
```
* **Response Example (201 Created)**:
```json
{
  "invoice_number": "INV-2026-001001",
  "grand_total": 139900.0,
  "down_payment": 5000.0,
  "remaining_balance": 134900.0,
  "payment_status": "partial",
  "sale_status": "completed"
}
```

---

## 💳 Payments & Collections API

### 1. Collect EMI Payment
* **Endpoint**: `POST /api/payments`
* **Content-Type**: `application/json`
* **Request Payload**:
```json
{
  "customer_id": "customer-uuid-string",
  "plan_id": "plan-uuid-string",
  "schedule_id": "schedule-uuid-string-optional",
  "amount": 22483.33,
  "payment_method": "UPI",
  "transaction_id": "TXN994801123",
  "remarks": "Dec EMI payment."
}
```
* **Response Example (201 Created)**:
```json
{
  "payment_id": "payment-uuid-string",
  "receipt_number": "RCT-2026-000025",
  "amount_paid": 22483.33,
  "status": "success"
}
```

---

## 📈 Reports & Analytics API

### 1. Reports Dashboard
* **Endpoint**: `GET /api/reports/dashboard`
* **Response Example (200 OK)**:
```json
{
  "total_sales": 300,
  "total_revenue": 829921.66,
  "total_outstanding": 533156.67,
  "total_stock_value": 3255000.00,
  "total_profit": 280600.00,
  "forecast": {
    "expected_monthly_revenue": 70489.78,
    "expected_collections_next_30_days": 115413.33,
    "expected_customer_growth": 0
  }
}
```
