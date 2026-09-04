"""
InstalmentSchedule model representing individual billing dates/terms under an instalment plan.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class InstalmentSchedule(db.Model):
    """
    Instalment Schedule table mapping.
    Links individual dates terms to instalment plans, logging amounts, paid quantities,
    balances, payment status flags, days overdue, and auditor remarks. Supports UUID keys.
    """
    __tablename__ = 'instalment_schedules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    plan_id = db.Column(db.String(36), db.ForeignKey('instalment_plans.id'), nullable=False)
    instalment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    
    # Financial breakdowns
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    
    payment_status = db.Column(db.String(20), nullable=False, default='pending') # pending, paid, partially_paid, overdue
    paid_date = db.Column(db.DateTime, nullable=True)
    days_overdue = db.Column(db.Integer, nullable=False, default=0)
    remarks = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    plan = db.relationship('InstalmentPlan', back_populates='schedules')

    def __repr__(self):
        return f"<InstalmentSchedule {self.instalment_number} for Plan ID {self.plan_id} (Status: {self.payment_status})>"
