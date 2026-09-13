import os
import secrets
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    """Base configuration class for Instalment Shop Management System."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Handle SQLAlchemy/Supabase scheme compatibility and host DNS resolution
    SQLALCHEMY_DATABASE_URI = None
    if DATABASE_URL and not DATABASE_URL.startswith('#') and 'YOUR_DB_PASSWORD' not in DATABASE_URL and 'your-db-password' not in DATABASE_URL:
        db_url = DATABASE_URL.replace("postgres://", "postgresql://", 1) if DATABASE_URL.startswith("postgres://") else DATABASE_URL
        try:
            parsed = urlparse(db_url)
            if parsed.hostname:
                # Fast DNS lookup check to ensure host is resolvable
                socket.gethostbyname(parsed.hostname)
                SQLALCHEMY_DATABASE_URI = db_url
        except Exception:
            # Host name lookup failed or invalid URI
            SQLALCHEMY_DATABASE_URI = None

    if not SQLALCHEMY_DATABASE_URI:
        # Fallback to SQLite for immediate local execution
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instalment_shop.db'
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File storage paths
    INVOICES_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'invoices')
    REPORTS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'reports')
    UPLOADS_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
