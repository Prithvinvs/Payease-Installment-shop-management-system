# Project Structure - Instalment Shop Management System

Comprehensive breakdown of the directory layout, module architecture, database models, route controllers, templates, and static assets for the **Instalment Shop Management System**.

---

## 📂 Directory Layout Overview

```
c:\Instalmentshopmanage\
├── 📄 app.py                  # Main Application Factory & Blueprint Registration
├── 📄 config.py               # Environment & Application Configuration
├── 📄 requirements.txt        # Python Dependencies
├── 📄 Dockerfile              # Container Build Definition
├── 📄 docker-compose.yml      # Multi-container Orchestration
├── 📄 Procfile                # Deployment Entrypoint
├── 📄 PROJECT_STRUCTURE.md    # Project Structure Documentation
├── 📄 website_structure.md    # Database Schema & Technical Architecture Spec
│
├── 📁 database/               # Database Engine & Connection Handling
│   ├── 📄 __init__.py         # SQLAlchemy & Database Initialization
│   └── 📄 supabase_client.py  # Supabase Integration Client
│
├── 📁 models/                 # SQLAlchemy Data Models (ORM Schema)
│   ├── 📄 user.py             # User Account Management
│   ├── 📄 role.py             # Role-Based Access Control (RBAC)
│   ├── 📄 customer.py         # Customer Profiles & Info
│   ├── 📄 customer_ledger.py  # Customer Financial Ledger Entries
│   ├── 📄 product.py          # Master Inventory Items
│   ├── 📄 category.py         # Product Classification Categories
│   ├── 📄 brand.py            # Product Brands & Manufacturers
│   ├── 📄 inventory_movement.py # Stock Movement Audit Logs
│   ├── 📄 sale.py             # Sales Headers & POS Transactions
│   ├── 📄 sale_item.py        # Sales Line Items Breakdown
│   ├── 📄 instalment_plan.py  # Instalment Financing Agreements
│   ├── 📄 instalment_schedule.py # Repayment Milestones & Due Dates
│   ├── 📄 payment.py          # Payment Collection Transactions
│   ├── 📄 payment_receipt.py  # Generated Receipt Metadata
│   ├── 📄 audit_log.py        # System Activity & Security Logs
│   ├── 📄 setting.py          # Dynamic Application Settings
│   └── 📄 password_reset.py   # Password Recovery Tokens
│
├── 📁 routes/                 # Controllers & APIs (Flask Blueprints)
│   ├── 📄 auth.py             # User Authentication Views (Login/Logout)
│   ├── 📄 users.py            # User Management & RBAC Administration
│   ├── 📄 dashboard.py        # Admin Overview & Analytics Views
│   ├── 📄 dashboard_api.py    # Real-time Metrics REST API
│   ├── 📄 customers.py        # Customer Web Views
│   ├── 📄 customers_api.py    # Customer REST API Endpoints
│   ├── 📄 products.py         # Product & Inventory Web Views
│   ├── 📄 products_api.py     # Product Search & Management REST API
│   ├── 📄 categories.py       # Product Category Management Views
│   ├── 📄 brands.py           # Brand Management Views
│   ├── 📄 inventory.py        # Stock Control & Movement Views
│   ├── 📄 sales.py            # POS Interface & Checkout Views
│   ├── 📄 sales_api.py        # Sales Transaction REST API
│   ├── 📄 instalments.py      # Instalment Plan Web Views
│   ├── 📄 instalments_api.py  # Instalment Schedule REST API
│   ├── 📄 payments.py         # Payment Collection Views
│   ├── 📄 payments_api.py     # Payment Processing REST API
│   ├── 📄 reports.py          # Analytical Reports Views
│   ├── 📄 reports_api.py      # Data Export & Report APIs
│   └── 📄 settings.py         # System Configuration Views
│
├── 📁 forms/                  # WTForms Input Validation Schemas
│   ├── 📄 customer.py         # Customer Form Validation Rules
│   └── 📄 product.py          # Product Form Validation Rules
│
├── 📁 services/               # Core Business Logic & Analytics
│   └── 📄 forecasting.py      # Demand & Cash Flow Forecasting Algorithms
│
├── 📁 utils/                  # Common Helpers & Middleware
│   ├── 📄 auth_decorators.py  # Authorization & Access Control Decorators
│   └── 📄 password_validators.py # Password Strength & Compliance Checks
│
├── 📁 templates/              # Jinja2 HTML UI Templates
│   ├── 📄 base.html           # Master Layout Template with Sidebar & Navbar
│   ├── 📄 dashboard.html      # Main Executive Dashboard View
│   ├── 📄 search.html         # Global System Search Results View
│   ├── 📄 403.html            # Forbidden Error Page
│   ├── 📄 404.html            # Not Found Error Page
│   ├── 📄 500.html            # Server Error Page
│   ├── 📁 auth/               # Login, Password Reset, Profile Views
│   ├── 📁 customers/          # List, Detail, Ledger, Add/Edit Views
│   ├── 📁 products/           # Product Catalog, Stock Alert, Edit Views
│   ├── 📁 sales/              # POS Terminal, Invoice Print, Sales History
│   ├── 📁 instalments/        # Plan Details, Schedule Printing, Calculators
│   ├── 📁 payments/           # Payment Processing & Receipt Generation
│   ├── 📁 reports/            # Financial & Inventory Analytics Views
│   ├── 📁 settings/           # Application Configuration Interface
│   └── 📁 users/              # User List & Permissions Management
│
├── 📁 static/                 # Static Assets
│   ├── 📁 css/                # Custom Stylesheets & Design System
│   ├── 📁 js/                 # Client-side Scripts & AJAX Modules
│   └── 📁 images/             # System Logos & Icons
│
├── 📁 scripts/                # Utility & Maintenance Scripts
│   ├── 📄 seed_fake_data.py   # Test Data Generation Script
│   └── 📄 generate_srs_pdf.py # SRS Document Export Script
│
├── 📁 supabase/               # Supabase Platform Infrastructure
│   └── 📁 migrations/         # SQL Schema Migration Scripts
│
└── 📁 invoices/, reports/, uploads/ # Generated PDFs, Exports & User Media
```

---

## 🛠️ Architecture Overview

### 1. Application Layer (`app.py`)
- **Factory Pattern**: Uses `create_app()` to support environment configuration.
- **Extensions**: Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF CSRF protection.
- **Blueprints**: Registers 20+ specialized module blueprints across Web UI and API routes.

### 2. Data & Model Layer (`models/` & `database/`)
- Built on SQLAlchemy ORM.
- Supports both local SQLite (`instalment_shop.db`) and PostgreSQL via Supabase.
- Full relational integrity for complex financial tracking (Customer Ledgers, Instalment Schedules, Sales Line Items, Payment Receipts).

### 3. Presentation Layer (`templates/` & `static/`)
- Server-rendered HTML powered by **Jinja2** with responsive design layouts ([`base.html`](file:///c:/Instalmentshopmanage/templates/base.html)).
- REST API layer ([`routes/*_api.py`](file:///c:/Instalmentshopmanage/routes)) enabling AJAX/dynamic POS workflows without full page reloads.
