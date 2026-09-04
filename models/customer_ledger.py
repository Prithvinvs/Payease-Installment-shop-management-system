"""
CustomerLedger model representing double-entry financial statements and accounts balances.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class CustomerLedger(db.Model):
    """
    Customer Ledger table mapping.
    Records debits (credit sales) and credits (payment collections) to track
    the running account balance of each customer. Supports UUID keys.
    """
    __tablename__ = 'customer_ledgers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    
    transaction_type = db.Column(db.String(20), nullable=False) # debit, credit
    reference_id = db.Column(db.String(36), nullable=False) # Sale ID or Payment ID
    description = db.Column(db.String(255), nullable=False)
    
    debit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    credit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    balance = db.Column(db.Numeric(10, 2), nullable=False) # running balance
    
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = db.relationship('Customer', foreign_keys=[customer_id])

    def __repr__(self):
        return f"<CustomerLedger {self.transaction_type} for Customer ID {self.customer_id} (Balance: {self.balance})>"
