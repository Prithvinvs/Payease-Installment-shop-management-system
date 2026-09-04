"""
Category model for grouping products.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class Category(db.Model):
    """
    Category table mapping.
    Organizes inventory items for classification and pricing. Supports UUID keys.
    """
    __tablename__ = 'categories'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    category_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active') # active, inactive
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    products = db.relationship('Product', back_populates='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name} ({self.category_code})>"
