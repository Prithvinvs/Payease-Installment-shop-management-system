"""
Product form and validation constraints.
"""
import os
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DecimalField, FileField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError

from models.product import Product

class ProductForm(FlaskForm):
    """
    Form validator for Product CRUD configurations.
    """
    product_name = StringField('Product Name', validators=[
        DataRequired(message="Product name is required."),
        Length(max=100)
    ])
    
    category_id = SelectField('Category', validators=[
        DataRequired(message="Category selection is required.")
    ])
    
    brand_id = SelectField('Brand', validators=[
        DataRequired(message="Brand selection is required.")
    ])
    
    description = TextAreaField('Description', validators=[Optional()])
    
    # Pricing Details
    purchase_price = DecimalField('Purchase Price', validators=[
        DataRequired(message="Purchase price is required."),
        NumberRange(min=0.01, message="Purchase price must be greater than zero.")
    ])
    
    selling_price = DecimalField('Selling Price', validators=[
        DataRequired(message="Selling price is required."),
        NumberRange(min=0.01, message="Selling price must be greater than zero.")
    ])
    
    gst_percentage = DecimalField('GST Percentage (%)', default=18.0, validators=[
        DataRequired(message="GST percentage is required."),
        NumberRange(min=0.0, max=100.0, message="GST percentage must be between 0 and 100.")
    ])
    
    discount_percentage = DecimalField('Discount Percentage (%)', default=0.0, validators=[
        Optional(),
        NumberRange(min=0.0, max=100.0, message="Discount must be between 0 and 100.")
    ])
    
    # Inventory details
    opening_stock = IntegerField('Opening Stock / Current Stock', default=0, validators=[
        Optional(),
        NumberRange(min=0, message="Opening stock cannot be negative.")
    ])
    
    minimum_stock = IntegerField('Minimum Stock Level', default=5, validators=[
        DataRequired(message="Minimum stock level is required."),
        NumberRange(min=0, message="Minimum stock level cannot be negative.")
    ])
    
    maximum_stock = IntegerField('Maximum Stock Level', default=100, validators=[
        DataRequired(message="Maximum stock level is required."),
        NumberRange(min=1, message="Maximum stock level must be at least 1.")
    ])
    
    unit = SelectField('Unit', choices=[
        ('pcs', 'pcs (Pieces)'),
        ('units', 'units'),
        ('boxes', 'boxes'),
        ('kg', 'kg (Kilograms)'),
        ('packs', 'packs')
    ], default='pcs', validators=[DataRequired()])
    
    product_image = FileField('Product Image')

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id', None)
        super(ProductForm, self).__init__(*args, **kwargs)

    def validate_selling_price(self, field):
        """
        Enforce business rule: Selling price must be greater than purchase price.
        """
        if self.purchase_price.data and field.data:
            if field.data <= self.purchase_price.data:
                raise ValidationError("Selling price must be greater than purchase price.")

    def validate_product_name(self, field):
        """
        Enforce business rule: Product names cannot be duplicated within the same brand.
        """
        if self.brand_id.data:
            query = Product.query.filter(
                Product.product_name.ilike(field.data),
                Product.brand_id == self.brand_id.data,
                Product.deleted_at == None
            )
            if self.product_id:
                query = query.filter(Product.id != self.product_id)
                
            existing = query.first()
            if existing:
                raise ValidationError("A product with this name is already registered under the selected brand.")

    def validate_product_image(self, field):
        """
        Restricts image formats to standard formats and sizes to <= 5MB.
        """
        if field.data and hasattr(field.data, 'filename') and field.data.filename:
            ext = field.data.filename.rsplit('.', 1)[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                raise ValidationError("Allowed image formats are: JPG, JPEG, PNG, WEBP.")
                
            try:
                field.data.seek(0, os.SEEK_END)
                size = field.data.tell()
                field.data.seek(0) # Reset file pointer
                if size > 5 * 1024 * 1024:
                    raise ValidationError("Product image size must be less than 5 MB.")
            except Exception:
                pass
