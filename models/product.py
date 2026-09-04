"""
Product model representing shop inventory items.
"""
from datetime import datetime
import uuid as uuid_pkg
from database import db

class Product(db.Model):
    """
    Product table mapping.
    Tracks product identifiers, barcode details, prices, GST tax values,
    discounts, unit metrics, stock levels, and creator audit fields. Supports soft deletion.
    """
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid_pkg.uuid4()))
    product_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False, index=True)
    qr_code = db.Column(db.String(255), nullable=True)
    
    product_name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # Pricing Details
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2), nullable=False)
    gst_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    
    # Inventory Counts
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock = db.Column(db.Integer, nullable=False, default=5)
    maximum_stock = db.Column(db.Integer, nullable=False, default=100)
    unit = db.Column(db.String(20), nullable=False, default='pcs') # pcs, units, boxes, kg
    
    product_image = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active') # active, inactive
    
    # Foreign Keys
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True) # Soft Delete indicator
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    category = db.relationship('Category', back_populates='products')
    brand = db.relationship('Brand', back_populates='products')
    movements = db.relationship('InventoryMovement', back_populates='product', cascade="all, delete-orphan", lazy=True)

    @property
    def is_low_stock(self):
        """
        Helper property returning whether stock is below warning threshold.
        """
        return self.current_stock <= self.minimum_stock and self.current_stock > 0

    @property
    def is_out_of_stock(self):
        """
        Helper checking if item is empty.
        """
        return self.current_stock <= 0

    @property
    def is_overstocked(self):
        """
        Helper checking if stock is above maximum threshold.
        """
        return self.current_stock > self.maximum_stock

    @property
    def stock_status(self):
        """
        Returns textual stock status classification.
        """
        if self.current_stock <= 0:
            return 'Out of Stock'
        elif self.current_stock <= self.minimum_stock:
            return 'Low Stock'
        elif self.current_stock > self.maximum_stock:
            return 'Overstock'
        return 'In Stock'

    @property
    def stock_value(self):
        """
        Calculates standard asset cost evaluation (selling_price * current_stock).
        """
        return float(self.selling_price) * self.current_stock

    def __repr__(self):
        return f"<Product {self.product_name} ({self.product_code})>"
