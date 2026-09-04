# Installation Guide

This guide details the step-by-step instructions for installing and running the PayEase Instalment Shop Management System locally.

---

## 📋 System Requirements
* **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
* **Python Version**: Python 3.11.x (Recommended) or 3.10+
* **Database**: SQLite (Included for development) or Supabase PostgreSQL (Production)

---

## ⚙️ Local Installation Steps

### 1. Clone or Extract Project
Extract the zip package or clone the repository to your local directory:
```bash
cd Instalmentshopmanage
```

### 2. Configure Virtual Environment
Create and activate a python virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all package requirements using `pip`:
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Configurations
Copy the sample environment file and configure variables:
```bash
copy .env.example .env
```
Inside `.env`, verify:
```ini
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-123
SQLALCHEMY_DATABASE_URI=sqlite:///instance/store.db
```

### 5. Initialize and Seed Database
Run the application startup command to automatically initialize tables and seed the complete demo database (100 Customers, 50 Products, 20 Categories, 15 Brands, 300 credit Sales, and 800 collections payments):
```bash
python app.py
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Default Credentials
Use the following accounts to test different roles:
1. **Super Admin** (Full admin controls & settings):
   * **Username**: `superadmin`
   * **Password**: `Admin@123`
2. **Admin** (Shop owner & reports):
   * **Username**: `admin`
   * **Password**: `Admin@123`
3. **Staff** (Checkout counter cashier):
   * **Username**: `staff`
   * **Password**: `Admin@123`
