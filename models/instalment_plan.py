"""
InstalmentPlan model representing payment plans for product credit sales.
"""
from datetime import datetime
import uuid as uuid_pkg
import decimal
from database import db

class InstalmentPlan(db.Model):
    """
    Instalment Plan table mapping.
    Manages outstanding balance summaries, EMI calculations, payment frequency, start/end dates,
    and active status logs. Supports UUID keys.
    """
    __tablename__ = 'instalment_plans'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    plan_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sale_id = db.Column(db.String(36), db.ForeignKey('sales.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    
    # Financial fields
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    down_payment = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    remaining_balance = db.Column(db.Numeric(10, 2), nullable=False)
    number_of_instalments = db.Column(db.Integer, nullable=False, default=6)
    monthly_emi = db.Column(db.Numeric(10, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0.00) # percentage
    processing_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
    # Timeline
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    first_due_date = db.Column(db.DateTime, nullable=False)
    last_due_date = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.String(20), nullable=False, default='active') # active, completed, overdue, cancelled
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    sale = db.relationship('Sale', back_populates='instalment_plan')
    customer = db.relationship('Customer', back_populates='instalment_plans')
    schedules = db.relationship('InstalmentSchedule', back_populates='plan', cascade="all, delete-orphan", order_by="InstalmentSchedule.instalment_number")

    @property
    def paid_amount(self):
        """
        Calculates total amount paid across all schedules.
        """
        total = decimal.Decimal('0.00')
        for item in self.schedules:
            if item.paid_amount is not None:
                total += decimal.Decimal(str(item.paid_amount))
        return total

    @property
    def outstanding_amount(self):
        """
        Calculates total outstanding balance.
        """
        return decimal.Decimal(str(self.remaining_balance)) - self.paid_amount

    @property
    def completed_count(self):
        return sum(1 for item in self.schedules if item.payment_status == 'paid')

    @property
    def pending_count(self):
        return sum(1 for item in self.schedules if item.payment_status == 'pending')

    @property
    def overdue_count(self):
        return sum(1 for item in self.schedules if item.payment_status == 'overdue')

    def __repr__(self):
        return f"<InstalmentPlan {self.plan_number} (Remaining: {self.outstanding_amount})>"
