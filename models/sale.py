"""
Sale model representing product sales and invoices.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class Sale(db.Model):
    """
    Sale table mapping.
    Links customers to product sales, recording invoice subtotal, taxes, discounts,
    down payments, outstanding balances, payment/sale statuses, and creators. Supports UUID keys.
    """
    __tablename__ = 'sales'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Financial Summary
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    grand_total = db.Column(db.Numeric(10, 2), nullable=False)
    down_payment = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    remaining_balance = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Statuses
    payment_status = db.Column(db.String(20), nullable=False, default='pending') # paid, partial, pending
    sale_status = db.Column(db.String(20), nullable=False, default='completed') # completed, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    customer = db.relationship('Customer', back_populates='sales')
    items = db.relationship('SaleItem', back_populates='sale', cascade="all, delete-orphan")
    instalment_plan = db.relationship('InstalmentPlan', back_populates='sale', uselist=False, lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', back_populates='sale', lazy=True, cascade="all, delete-orphan")
    creator = db.relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f"<Sale {self.invoice_number} (Total: {self.grand_total}, Status: {self.sale_status})>"
