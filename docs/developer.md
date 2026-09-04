# Developer Documentation

This document explains the software architecture, design patterns, file directory organization, and extension guidelines for the PayEase codebase.

---

## 🏗️ Architecture Design (MVC)

The system is structured using the **Model-View-Controller (MVC)** architectural pattern, divided into clean layers:

```
        ┌────────────────────────────────────────────────────────┐
        │                        BROWSER                         │
        └───────────────────────────┬────────────────────────────┘
                                    │ HTTP Requests
                                    ▼
        ┌────────────────────────────────────────────────────────┐
        │                   CONTROLLERS / VIEWS                  │
        │               (Flask Blueprints in routes/)            │
        └───────────────────────────┬────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
        ┌───────────────────┐               ┌───────────────────┐
        │   BUSINESS LOGIC  │               │  DATABASE MODELS  │
        │    (services/)    │               │     (models/)     │
        └───────────────────┘               └───────────────────┘
```

1. **Models (`models/`)**: SQLAlchemy classes defining table constraints, relationships, properties, and getters (e.g. `Product`, `Customer`, `InstalmentPlan`).
2. **Views & Controllers (`routes/`)**:
   * Web controllers serving compiled HTML5 sheets (under `templates/`).
   * REST endpoints (`*_api.py` blueprints) serving JSON payloads.
3. **Services (`services/`)**: Standalone Python modules handling complex business math or file generations (e.g. `services/forecasting.py`).
4. **Forms (`forms/`)**: Form data validators using WTForms.

---

## 📂 Folder Structure

```
instalment_shop_management/
├── app.py                     # Application factory configures error handlers & engines.
├── config.py                  # Environment config parsing.
├── database/                  # SQLite tables init and 1,600+ database seeder.
├── models/                    # SQLAlchemy database model classes.
├── routes/                    # Web views blueprints and API blueprints.
├── services/                  # Projections forecasting business logic.
├── forms/                     # Flask-WTF input validation classes.
├── templates/                 # HTML templates organized by module.
├── static/                    # CSS stylesheets, Javascript main scripts, and image assets.
├── backups/                   # Directory containing SQLite timestamped database copies.
├── docs/                      # Admin, user, and developer guides.
└── uploads/                   # Store custom brand logo uploads.
```

---

## 🧪 Testing Guidelines

Verify the modules using python command execution:

### 1. Authentication & Security test
```bash
python C:\Users\prith\.gemini\antigravity\brain\c27b4f37-074d-4b03-b546-c512020701c4\scratch\verify_auth.py
```

### 2. Customers operations test
```bash
python C:\Users\prith\.gemini\antigravity\brain\c27b4f37-074d-4b03-b546-c512020701c4\scratch\verify_customers.py
```

### 3. Sales & Billings check
```bash
python C:\Users\prith\.gemini\antigravity\brain\c27b4f37-074d-4b03-b546-c512020701c4\scratch\verify_sales.py
```

### 4. Payments, Ledgers, & Backups check
```bash
python C:\Users\prith\.gemini\antigravity\brain\c27b4f37-074d-4b03-b546-c512020701c4\scratch\verify_production.py
```
