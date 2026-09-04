# Maintenance & Troubleshooting Guide

This guide describes routine database maintenance protocols and troubleshooting procedures for common application states.

---

## 🛠️ Database Migrations (Flask-Migrate)

When modifying model files (under `models/`), execute the following commands to apply migrations cleanly:
```bash
# Initialize migration tracking (runs once at project start)
flask db init

# Detect model schema shifts and compile migration script
flask db migrate -m "Added column X to table Y"

# Apply migrations to update active database schema
flask db upgrade
```

---

## 🔍 Troubleshooting Scenarios

### 1. Database Locked Error (`sqlite3.OperationalError: database is locked`)
* **Cause**: Concurrent write requests or open connections blocking access.
* **Resolution**:
  1. Restart the Flask server.
  2. If running inside a container, restart docker: `docker-compose restart`.
  3. Ensure no local SQLite viewers are holding write-locks on `store.db`.

### 2. Flash of Light Theme in Dark Mode
* **Cause**: Theme settings applied after page load.
* **Resolution**: Ensure the synchronous theme loader script block is present in the `<head>` of `templates/base.html`.

### 3. CSV/Excel Exports crash on special characters
* **Cause**: Encoding mismatches inside terminal or download streams.
* **Resolution**: Standardize exports on `io.StringIO` streaming with UTF-8 outputs.

---

## 📋 Recommended Maintenance Schedule
* **Daily**: Verify automated backups are running.
* **Weekly**: Download a backup copy offsite.
* **Monthly**: Audit trail review (inspecting logged user sessions, changes, and failed access attempts).
