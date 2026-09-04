"""
InventoryMovement model representing stock updates and adjustments.
"""
from datetime import datetime
from database import db

class InventoryMovement(db.Model):
    """
    Inventory Movements table mapping.
    Keeps historical records of every stock adjustment (In, Out, Adjustments, Sales, Returns).
    """
    __tablename__ = 'inventory_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False) # Stock In, Stock Out, Adjustment, Sales, Return
    quantity = db.Column(db.Integer, nullable=False) # Change amount (positive)
    previous_stock = db.Column(db.Integer, nullable=False)
    new_stock = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.String(255), nullable=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = db.relationship('Product', back_populates='movements')
    user = db.relationship('User')

    def __repr__(self):
        return f"<InventoryMovement {self.id} (Product: {self.product_id}, Type: {self.movement_type})>"
