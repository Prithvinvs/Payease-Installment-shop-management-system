"""
Payment model representing cash collections and receipts against credit sales.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class Payment(db.Model):
    """
    Payment table mapping.
    Tracks complete meta details of customer cash collections, including methods,
    bank descriptors, operator references, and custom notes. Supports UUID keys.
    """
    __tablename__ = 'payments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    plan_id = db.Column(db.String(36), db.ForeignKey('instalment_plans.id'), nullable=True)
    schedule_id = db.Column(db.String(36), db.ForeignKey('instalment_schedules.id'), nullable=True)
    sale_id = db.Column(db.String(36), db.ForeignKey('sales.id'), nullable=True)
    invoice_number = db.Column(db.String(50), nullable=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    
    # Financial fields
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    payment_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Types and Methods
    payment_type = db.Column(db.String(50), nullable=False, default='EMI Payment') # EMI Payment, Full Payment, Partial Payment, Advance Payment, etc.
    payment_method = db.Column(db.String(50), nullable=False, default='Cash') # Cash, UPI, Credit Card, Debit Card, Net Banking, Bank Transfer, Cheque
    reference_number = db.Column(db.String(100), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    transaction_id = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    
    # Operator
    received_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    payment_status = db.Column(db.String(20), nullable=False, default='paid') # paid, reversed/refunded
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = db.relationship('Customer', back_populates='payments')
    sale = db.relationship('Sale', back_populates='payments')
    plan = db.relationship('InstalmentPlan', foreign_keys=[plan_id])
    schedule = db.relationship('InstalmentSchedule', foreign_keys=[schedule_id])
    receipt = db.relationship('PaymentReceipt', back_populates='payment', uselist=False, cascade="all, delete-orphan")
    creator = db.relationship('User', foreign_keys=[received_by])

    # Backward compatibility mappings
    @property
    def status(self):
        return self.payment_status

    @status.setter
    def status(self, value):
        self.payment_status = value

    def __repr__(self):
        return f"<Payment {self.receipt_number} (Amount: {self.payment_amount})>"
