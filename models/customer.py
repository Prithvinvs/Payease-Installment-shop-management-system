"""
Customer model representing credit and instalment-paying clients.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class Customer(db.Model):
    """
    Customer table mapping.
    Records extensive credit customer details, billing addresses, status indicators,
    and audit tracking variables. Supports soft deletion.
    """
    __tablename__ = 'customers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    customer_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    alternate_phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    
    # Address details
    address_line1 = db.Column(db.String(100), nullable=False)
    address_line2 = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False, default='India')
    
    # Additional demographics
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(15), nullable=False)
    occupation = db.Column(db.String(50), nullable=True)
    aadhaar_number = db.Column(db.String(20), nullable=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active') # active, inactive
    
    # Audit log indicators
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True) # Soft Delete indicator
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    sales = db.relationship('Sale', back_populates='customer', lazy=True)
    payments = db.relationship('Payment', back_populates='customer', lazy=True)
    instalment_plans = db.relationship('InstalmentPlan', back_populates='customer', lazy=True)

    @property
    def outstanding_balance(self):
        """
        Dynamically calculates outstanding payments balance for this customer.
        Sums up the unpaid balances of all active instalment plans.
        """
        balance = 0.0
        for plan in self.instalment_plans:
            if plan.status in ['active', 'overdue']:
                balance += float(plan.outstanding_amount)
        return balance

    @property
    def total_purchases(self):
        """
        Sums up total invoice amounts purchased.
        """
        return sum(float(sale.grand_total) for sale in self.sales if sale.sale_status != 'cancelled')

    @property
    def total_payments(self):
        """
        Sums up total paid cash receipts.
        """
        return sum(float(pay.payment_amount) for pay in self.payments if pay.status == 'paid')

    def __repr__(self):
        return f"<Customer {self.full_name} ({self.customer_code})>"
