"""
User model representing system operators/administrators.
Implements Flask-Login UserMixin for session management and RBAC.
"""
from datetime import datetime
import uuid as uuid_pkg
import bcrypt
from flask_login import UserMixin
from database import db

class User(db.Model, UserMixin):
    """
    User model for authentication, role-based authorization, activity tracking,
    brute-force prevention, and soft delete.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid_pkg.uuid4()))
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active') # active, inactive
    
    # Brute force protection
    login_attempts = db.Column(db.Integer, nullable=False, default=0)
    lockout_until = db.Column(db.DateTime, nullable=True)
    
    # Session / Tracking
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True) # Soft delete timestamp

    # Relationships
    role = db.relationship('Role', back_populates='users')

    def set_password(self, password):
        """
        Hashes password using bcrypt and stores it in password_hash.
        """
        # bcrypt requires bytes for hashing
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')

    def check_password(self, password):
        """
        Verifies a plaintext password against the stored bcrypt hash.
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False

    @property
    def is_active(self):
        """
        Overrides UserMixin.is_active to check status and soft-delete flags.
        Flask-Login uses this property to permit or reject logins.
        """
        return self.status == 'active' and self.deleted_at is None

    @property
    def is_locked(self):
        """
        Checks if the user account is currently locked out due to brute-force protection.
        """
        if self.lockout_until and self.lockout_until > datetime.utcnow():
            return True
        return False

    def __repr__(self):
        return f"<User {self.username} (Role ID: {self.role_id})>"
