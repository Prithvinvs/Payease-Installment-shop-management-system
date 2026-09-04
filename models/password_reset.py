"""
PasswordResetToken model for handling secure, temporary recovery tokens.
"""
from datetime import datetime, timedelta
import secrets
import hashlib
from database import db

class PasswordResetToken(db.Model):
    """
    Password Reset Tokens table.
    Stores cryptographic hashes of reset tokens sent via email.
    """
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('reset_tokens', lazy=True, cascade="all, delete-orphan"))

    @staticmethod
    def generate_token_pair(user_id, lifetime_minutes=30):
        """
        Generates a (raw_token, token_hash_record) pair.
        The raw_token is sent to the user, and the token_hash_record is saved to the db.
        """
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(minutes=lifetime_minutes)
        
        record = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        return raw_token, record

    @classmethod
    def verify_token(cls, raw_token):
        """
        Finds a valid, unexpired reset token matching the raw token.
        """
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        record = cls.query.filter_by(token_hash=token_hash).first()
        
        if record and record.used_at is None and record.expires_at > datetime.utcnow():
            return record
        return None

    def mark_as_used(self):
        """
        Marks this token as consumed.
        """
        self.used_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
