# PayEase - Instalment Shop Management System

PayEase is a production-ready Web ERP application tailored for small to medium shop owners to manage credit sales, customer instalments, invoice generation, receipts, and collection analytics.

This project uses Python Flask, SQLAlchemy, Supabase PostgreSQL, and Bootstrap 5.

---

## 📁 Folder Structure

```
c:\Instalmentshopmanage\
├── app.py                      # Application Factory and startup entrypoint
├── config.py                   # Environment and database config settings
├── requirements.txt            # System dependencies
├── .env                        # Local secret configurations (git-ignored)
├── .env.example                # Configuration template
├── .gitignore                  # Git tracking exclusions
├── README.md                   # Setup guide and instructions
│
├── database/                   # Database instance and startup hooks
│   └── __init__.py
│
├── models/                     # SQLAlchemy Models mapping SQL schemas
│   ├── __init__.py
│   └── user.py                 # System Operators and roles table mapping
│
├── routes/                     # Modular Blueprints
│   ├── __init__.py
│   ├── auth.py                 # Sign-in/Sign-out controller infrastructure
│   └── dashboard.py            # Overview dashboard controller
│
├── services/                   # Business logic layer
│   └── .gitkeep
│
├── utils/                      # Common utilities (converters, validators)
│   └── .gitkeep
│
├── templates/                  # Jinja2 template components
│   ├── base.html               # Parent ERP layout structure (responsive sidebar, navbar)
│   ├── dashboard.html          # Performance statistics and transactions board
│   ├── 404.html                # Not Found error page
│   ├── 500.html                # Server Exception page
│   └── auth/
│       └── login.html          # Login card interface
│
├── static/                     # Web resources
│   ├── css/
│   │   └── style.css           # Premium stylesheet with HSL colors & dark mode variables
│   ├── js/
│   │   ├── main.js             # Theme swapping, collapsible side navigation, UI events
│   │   └── dashboard.js        # Dynamic theme-aware Chart.js scripts
│   └── images/
│       └── .gitkeep
│
├── invoices/                   # Generated credit sales invoices (git-ignored)
├── reports/                    # Generated weekly/monthly reports (git-ignored)
└── uploads/                    # Profile/product attachment uploads (git-ignored)
```

---

## ⚡ Tech Stack

* **Backend**: Python 3, Flask, Flask-WTF, Flask-Login, Flask-SQLAlchemy, Flask-Migrate
* **Frontend**: HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Bootstrap Icons, Chart.js
* **Database**: Supabase PostgreSQL (with an out-of-the-box SQLite local fallback)

---

## 🚀 Setup & Local Execution

Follow these steps to run the application locally on your system:

### 1. Prerequisite: Python
Make sure you have **Python 3.8+** installed. You can check this by running:
```bash
python --version
```

### 2. Clone/Open the Workspace and Setup Virtual Environment
Navigate to the project root directory and create a virtual environment:
```bash
cd c:\Instalmentshopmanage
python -m venv venv
```

Activate the virtual environment:
* **Windows (Command Prompt)**:
  ```cmd
  venv\Scripts\activate
  ```
* **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
Install all package requirements defined in the file:
```bash
pip install -r requirements.txt
```

### 4. Configuration (.env)
The environment variables have been pre-set for immediate development use in `.env`.
* If you want to connect to a **Supabase PostgreSQL database**, open `.env`, uncomment `DATABASE_URL` and insert your Supabase connection string:
  ```env
  DATABASE_URL=postgresql://postgres.[your-supabase-ref-id]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
  ```
* If `DATABASE_URL` is omitted, PayEase will automatically initialize an SQLite local database `instalment_shop.db` in the workspace root, making it run instantly without further configurations!

### 5. Run the Server
Launch the Flask development server:
```bash
python app.py
```
Or use the Flask CLI:
```bash
flask run
```

Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 Default Credentials
Use the following credentials to log in and test different access levels:
* **Super Admin**: Username `superadmin` | Password `Admin@123`
* **Admin**: Username `admin` | Password `Admin@123`
* **Staff**: Username `staff` | Password `Admin@123`

---

## 📄 Documentation Indices
Refer to the following guides in the `docs/` directory for detailed setup and guidelines:
* [Installation Guide](file:///c:/Instalmentshopmanage/docs/installation.md)
* [Deployment Guide](file:///c:/Instalmentshopmanage/docs/deployment.md)
* [Developer Guide](file:///c:/Instalmentshopmanage/docs/developer.md)
* [API Documentation](file:///c:/Instalmentshopmanage/docs/api.md)
* [Database Documentation](file:///c:/Instalmentshopmanage/docs/database.md)
* [User Manual](file:///c:/Instalmentshopmanage/docs/user_manual.md)
* [Administrator Manual](file:///c:/Instalmentshopmanage/docs/admin_manual.md)
* [Maintenance & Troubleshooting Guide](file:///c:/Instalmentshopmanage/docs/maintenance.md)
