"""
Settings and Backups management Web Blueprint.
Provides transactional configuration panels and SQLite backups administration.
"""
import os
import sqlite3
import shutil
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from database import db
from models.setting import Setting
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

BACKUPS_DIR = 'backups'

def ensure_backups_dir():
    if not os.path.exists(BACKUPS_DIR):
        os.makedirs(BACKUPS_DIR)

def is_sqlite_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            return header == b'SQLite format 3\x00'
    except Exception:
        return False

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def index():
    """
    GET/POST /settings
    Updates shop details and prefixes. Listing active database backups.
    """
    ensure_backups_dir()
    
    if request.method == 'POST':
        # Restrict save/updates to Super Admin only
        if current_user.role.role_name != 'Super Admin':
            flash("Authorization restriction: Only Super Admin can modify shop settings.", "danger")
            return redirect(url_for('settings.index'))
            
        # Update settings key-values
        keys = [
            'shop_name', 'shop_address', 'shop_phone', 'shop_email',
            'gst_number', 'currency', 'timezone', 'date_format',
            'invoice_prefix', 'receipt_prefix', 'backup_schedule', 'theme'
        ]
        
        # Log old vs new settings values for Audit Trail
        changes_logged = []
        for key in keys:
            old_val = Setting.get_val(key, "")
            new_val = request.form.get(key, "").strip()
            if old_val != new_val:
                Setting.set_val(key, new_val)
                changes_logged.append(f"{key}: '{old_val}' -> '{new_val}'")
                
        if changes_logged:
            AuditLog.log(
                action="settings_update",
                user_id=current_user.id,
                username=current_user.username
            )
            flash("Settings updated successfully.", "success")
        return redirect(url_for('settings.index'))
        
    # Get current configurations
    config_keys = [
        ('shop_name', 'PayEase Store'),
        ('shop_address', 'MG Road, Bangalore, India'),
        ('shop_phone', '+91 98765 43210'),
        ('shop_email', 'info@payease.com'),
        ('gst_number', '29AAAAA1111A1Z1'),
        ('currency', 'INR'),
        ('timezone', 'Asia/Kolkata'),
        ('date_format', '%d-%b-%Y'),
        ('invoice_prefix', 'INV-'),
        ('receipt_prefix', 'RCT-'),
        ('backup_schedule', 'daily'),
        ('theme', 'light')
    ]
    
    current_settings = {}
    for key, default in config_keys:
        current_settings[key] = Setting.get_val(key, default)
        
    # List backups in directory
    backups_list = []
    if os.path.exists(BACKUPS_DIR):
        for f in os.listdir(BACKUPS_DIR):
            if f.endswith('.db'):
                path = os.path.join(BACKUPS_DIR, f)
                stat = os.stat(path)
                backups_list.append({
                    'filename': f,
                    'size': f"{stat.st_size / 1024 / 1024:.2f} MB",
                    'created_at': datetime.fromtimestamp(stat.st_mtime).strftime('%d-%b-%Y %H:%M')
                })
                
    backups_list.sort(key=lambda x: x['filename'], reverse=True)
    
    return render_template(
        'settings/settings.html',
        settings=current_settings,
        backups=backups_list
    )


@settings_bp.route('/backup/create', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def create_backup():
    """
    POST /settings/backup/create
    Creates a transaction-safe SQLite database backup file.
    """
    ensure_backups_dir()
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not db_path or db_path == ':memory:':
        # Default fallback
        db_path = 'instance/store.db'
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(BACKUPS_DIR, backup_filename)
    
    try:
        # SQLite transaction safe backup copy
        src_conn = sqlite3.connect(db_path)
        dest_conn = sqlite3.connect(backup_path)
        with dest_conn:
            src_conn.backup(dest_conn)
        dest_conn.close()
        src_conn.close()
        
        AuditLog.log(
            action=f"backup_create: {backup_filename}",
            user_id=current_user.id,
            username=current_user.username
        )
        flash(f"Manual database backup {backup_filename} created successfully.", "success")
    except Exception as e:
        flash(f"Failed to create database backup: {str(e)}", "danger")
        
    return redirect(url_for('settings.index'))


@settings_bp.route('/backup/download/<string:filename>', methods=['GET'])
@login_required
@role_required(['Super Admin', 'Admin'])
def download_backup(filename):
    """
    GET /settings/backup/download/<filename>
    Downloads a database backup file.
    """
    filename = secure_filename(filename)
    backup_path = os.path.join(BACKUPS_DIR, filename)
    if not os.path.exists(backup_path):
        flash("Requested backup file not found.", "danger")
        return redirect(url_for('settings.index'))
        
    AuditLog.log(
        action=f"backup_download: {filename}",
        user_id=current_user.id,
        username=current_user.username
    )
    return send_from_directory(BACKUPS_DIR, filename, as_attachment=True)


@settings_bp.route('/backup/restore/<string:filename>', methods=['POST'])
@login_required
@role_required(['Super Admin'])
def restore_backup(filename):
    """
    POST /settings/backup/restore/<filename>
    Restores the database to a selected backup version.
    """
    filename = secure_filename(filename)
    backup_path = os.path.join(BACKUPS_DIR, filename)
    if not os.path.exists(backup_path):
        flash("Selected backup file not found.", "danger")
        return redirect(url_for('settings.index'))
        
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not db_path or db_path == ':memory:':
        db_path = 'instance/store.db'
        
    try:
        # Close all active SQLAlchemy sessions to unlock the DB file
        db.session.remove()
        
        # SQLite transaction safe restore copy
        src_conn = sqlite3.connect(backup_path)
        dest_conn = sqlite3.connect(db_path)
        with dest_conn:
            src_conn.backup(dest_conn)
        dest_conn.close()
        src_conn.close()
        
        AuditLog.log(
            action=f"backup_restore: {filename}",
            user_id=current_user.id,
            username=current_user.username
        )
        flash(f"Database successfully restored to backup version {filename}.", "success")
    except Exception as e:
        flash(f"Failed to restore database: {str(e)}", "danger")
        
    return redirect(url_for('settings.index'))


@settings_bp.route('/backup/delete/<string:filename>', methods=['POST'])
@login_required
@role_required(['Super Admin'])
def delete_backup(filename):
    """
    POST /settings/backup/delete/<filename>
    Deletes a database backup file.
    """
    filename = secure_filename(filename)
    backup_path = os.path.join(BACKUPS_DIR, filename)
    if os.path.exists(backup_path):
        os.remove(backup_path)
        AuditLog.log(
            action=f"backup_delete: {filename}",
            user_id=current_user.id,
            username=current_user.username
        )
        flash(f"Backup file {filename} deleted successfully.", "success")
    else:
        flash("Selected backup file not found.", "danger")
        
    return redirect(url_for('settings.index'))


@settings_bp.route('/backup/upload', methods=['POST'])
@login_required
@role_required(['Super Admin'])
def upload_backup():
    """
    POST /settings/backup/upload
    Accepts an uploaded database backup file and restores it.
    """
    if 'backup_file' not in request.files:
        flash("No backup file uploaded.", "danger")
        return redirect(url_for('settings.index'))
        
    file = request.files['backup_file']
    if file.filename == '':
        flash("No backup file selected.", "danger")
        return redirect(url_for('settings.index'))
        
    if file:
        filename = secure_filename(file.filename)
        if not filename.endswith('.db'):
            flash("Invalid backup file extension. Must be a '.db' file.", "danger")
            return redirect(url_for('settings.index'))
            
        ensure_backups_dir()
        temp_path = os.path.join(BACKUPS_DIR, f"temp_upload_{filename}")
        file.save(temp_path)
        
        # Verify uploaded file is a valid SQLite DB file
        if not is_sqlite_file(temp_path):
            os.remove(temp_path)
            flash("Uploaded file is not a valid SQLite database.", "danger")
            return redirect(url_for('settings.index'))
            
        # Rename to permanent upload file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_filename = f"upload_{timestamp}_{filename}"
        final_path = os.path.join(BACKUPS_DIR, final_filename)
        os.rename(temp_path, final_path)
        
        # Perform restore
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not db_path or db_path == ':memory:':
            db_path = 'instance/store.db'
            
        try:
            db.session.remove()
            src_conn = sqlite3.connect(final_path)
            dest_conn = sqlite3.connect(db_path)
            with dest_conn:
                src_conn.backup(dest_conn)
            dest_conn.close()
            src_conn.close()
            
            AuditLog.log(
                action=f"backup_upload_restore: {final_filename}",
                user_id=current_user.id,
                username=current_user.username
            )
            flash(f"Database successfully restored from uploaded backup {final_filename}.", "success")
        except Exception as e:
            flash(f"Failed to restore database from upload: {str(e)}", "danger")
            
    return redirect(url_for('settings.index'))
