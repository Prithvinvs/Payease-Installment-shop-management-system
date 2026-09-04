"""
PaymentReceipt model representing printed receipt details for payments.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class PaymentReceipt(db.Model):
    """
    Payment Receipt table mapping.
    Records receipt copies corresponding to payments. Supports UUID keys.
    """
    __tablename__ = 'payment_receipts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    payment_id = db.Column(db.String(36), db.ForeignKey('payments.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    
    receipt_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    amount_received = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    generated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    payment = db.relationship('Payment', back_populates='receipt')
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    creator = db.relationship('User', foreign_keys=[generated_by])

    def __repr__(self):
        return f"<PaymentReceipt {self.receipt_number} (Amount: {self.amount_received})>"
