"""
Product & Inventory REST API blueprint.
Provides JSON APIs for search fields autocomplete, mobile clients, and dashboard widgets.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from database import db
from models.product import Product
from models.category import Category
from models.brand import Brand
from models.inventory_movement import InventoryMovement

products_api_bp = Blueprint('products_api', __name__, url_prefix='/api')

def product_to_dict(p):
    return {
        'id': p.id,
        'product_code': p.product_code,
        'barcode': p.barcode,
        'qr_code': p.qr_code or '',
        'product_name': p.product_name,
        'description': p.description or '',
        'purchase_price': float(p.purchase_price),
        'selling_price': float(p.selling_price),
        'gst_percentage': float(p.gst_percentage),
        'discount_percentage': float(p.discount_percentage),
        'current_stock': p.current_stock,
        'minimum_stock': p.minimum_stock,
        'maximum_stock': p.maximum_stock,
        'unit': p.unit,
        'product_image': p.product_image or '',
        'status': p.status,
        'category': p.category.name,
        'brand': p.brand.brand_name,
        'is_low_stock': p.is_low_stock,
        'is_out_of_stock': p.is_out_of_stock,
        'stock_status': p.stock_status,
        'stock_value': p.stock_value
    }

@products_api_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """
    GET /api/products
    Returns all active non-deleted products list.
    """
    products = Product.query.filter_by(deleted_at=None).all()
    return jsonify([product_to_dict(p) for p in products]), 200

@products_api_bp.route('/products/<string:id>', methods=['GET'])
@login_required
def get_product(id):
    """
    GET /api/products/<id>
    """
    p = Product.query.filter_by(id=id, deleted_at=None).first()
    if not p:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product_to_dict(p)), 200

@products_api_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """
    GET /api/categories
    """
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'category_code': c.category_code,
        'name': c.name,
        'description': c.description or '',
        'status': c.status
    } for c in categories]), 200

@products_api_bp.route('/brands', methods=['GET'])
@login_required
def get_brands():
    """
    GET /api/brands
    """
    brands = Brand.query.all()
    return jsonify([{
        'id': b.id,
        'brand_name': b.brand_name,
        'description': b.description or '',
        'status': b.status
    } for b in brands]), 200

@products_api_bp.route('/inventory', methods=['GET'])
@login_required
def get_inventory():
    """
    GET /api/inventory
    Returns valuation list of inventory.
    """
    products = Product.query.filter_by(deleted_at=None).all()
    total_val = sum(p.stock_value for p in products)
    
    return jsonify({
        'total_valuation': total_val,
        'total_products_count': len(products),
        'items': [product_to_dict(p) for p in products]
    }), 200

@products_api_bp.route('/stock-movements', methods=['GET'])
@login_required
def get_movements():
    """
    GET /api/stock-movements
    """
    movements = InventoryMovement.query.order_by(InventoryMovement.created_at.desc()).all()
    return jsonify([{
        'id': m.id,
        'product_name': m.product.product_name,
        'product_code': m.product.product_code,
        'movement_type': m.movement_type,
        'quantity': m.quantity,
        'previous_stock': m.previous_stock,
        'new_stock': m.new_stock,
        'remarks': m.remarks or '',
        'user': m.user.username if m.user else 'System',
        'date': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for m in movements]), 200

@products_api_bp.route('/products/search', methods=['GET'])
@login_required
def search_products():
    """
    GET /api/products/search?q=value
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([]), 200
        
    results = Product.query.filter(
        Product.deleted_at == None
    ).filter(
        (Product.product_name.ilike(f"%{q}%")) |
        (Product.product_code.ilike(f"%{q}%")) |
        (Product.barcode.ilike(f"%{q}%"))
    ).limit(20).all()
    
    return jsonify([product_to_dict(p) for p in results]), 200
