"""
AuditLog model for logging security and administrative events.
"""
from datetime import datetime
from flask import request
from database import db

class AuditLog(db.Model):
    """
    Audit log table.
    Tracks user sessions, changes, and failed access attempts.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username = db.Column(db.String(120), nullable=True)
    action = db.Column(db.String(50), nullable=False, index=True) # e.g. login_success, login_failed, logout, etc.
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))

    @staticmethod
    def log(action, user_id=None, username=None):
        """
        Helper method to log an action with automatic IP and User-Agent extraction.
        """
        ip_address = request.remote_addr if request else '127.0.0.1'
        # Handle proxy headers if behind a load balancer/Supabase Pooler
        if request and request.headers.getlist("X-Forwarded-For"):
            ip_address = request.headers.getlist("X-Forwarded-For")[0]
            
        user_agent = request.headers.get('User-Agent', '')[:255] if request else 'System'
        
        log_entry = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

    def __repr__(self):
        return f"<AuditLog {self.action} by User {self.username} at {self.timestamp}>"
