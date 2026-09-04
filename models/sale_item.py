"""
SaleItem model representing items sold within a sales invoice.
"""
from database import db

class SaleItem(db.Model):
    """
    Sale Items table mapping.
    Links sales to products, recording quantity, unit cost, taxes, discounts, and total price.
    """
    __tablename__ = 'sale_items'

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.String(36), db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), nullable=False, default=0.0) # Percentage discount
    tax = db.Column(db.Numeric(5, 2), nullable=False, default=0.0) # GST percentage
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    sale = db.relationship('Sale', back_populates='items')
    product = db.relationship('Product')

    def __repr__(self):
        return f"<SaleItem {self.id} (Sale: {self.sale_id}, Product: {self.product_id}, Qty: {self.quantity})>"
