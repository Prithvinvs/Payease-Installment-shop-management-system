# Administrator Manual

This manual provides instructions for administrators managing system settings, users, and backup configurations.

---

## 👥 User Account Management

To add or manage operator profiles (Super Admin, Admin, Staff):
1. Log in as a **Super Admin**.
2. Navigate to **Users** in the sidebar.
3. Click **Add User** and fill in the username, email, full name, and assign a role (Super Admin, Admin, or Staff).
4. Save the user.

---

## ⚙️ Shop Profile Configurations

Configure shop parameters, invoice numbering sequences, and localization codes:
1. Log in as a **Super Admin**.
2. Click **Settings & Backups** in the sidebar navigation.
3. Under **Store Configurations**, edit:
   * **Shop Name** (reloads globally in headers/footers)
   * **GST Number**
   * **Receipt/Invoice Prefixes** (modifies sequence generators)
   * **Currency & Timezone**
4. Click **Save Configuration**.

---

## 💾 Backups & Database Recovery

The backup engine executes transaction-safe database snapshots using SQLite's native `.backup()` API.

### 1. Trigger Manual Backup
1. Click **Settings & Backups**.
2. Under **Database Backups**, click **Create Manual Backup**.
3. A timestamped `.db` file is saved inside the `backups/` directory (e.g. `backup_20260712_233200.db`).

### 2. Download Backup File
1. Under **Backups Ledger**, find the target backup row.
2. Click the blue **Download** button to save the file locally.

### 3. Restore Database to a Backup Version
> [!CAUTION]
> Restoring a database overwrites all current system records. Ensure you save a manual backup of the current state before restoring.
1. Locate the target version in the ledger.
2. Click the orange **Restore** icon.
3. Confirm the confirmation popup. The system will reload tables cleanly.

### 4. Upload and Restore External Backup
1. Under **Upload and Restore Backup**, click **Choose File** and select your `.db` file.
2. Click **Upload & Restore**.
3. The system validates the SQLite format and reloads data.
