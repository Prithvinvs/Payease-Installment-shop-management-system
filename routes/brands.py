"""
Brand management routes blueprint.
Handles CRUD actions for product brands.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from database import db
from models.brand import Brand
from models.product import Product
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

brands_bp = Blueprint('brands', __name__, url_prefix='/brands')

@brands_bp.route('/')
@login_required
def index():
    """
    Renders list of all product brands.
    """
    brands = Brand.query.order_by(Brand.brand_name).all()
    return render_template('brands/list.html', brands=brands)

@brands_bp.route('/add', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def add():
    """
    Adds a new product brand.
    """
    name = request.form.get('brand_name', '').strip()
    desc = request.form.get('description', '').strip()
    
    if not name:
        flash("Brand name is required.", "danger")
        return redirect(url_for('brands.index'))
        
    existing = Brand.query.filter(Brand.brand_name.ilike(name)).first()
    if existing:
        flash(f"A brand with name '{name}' already exists.", "danger")
        return redirect(url_for('brands.index'))
        
    brand = Brand(
        brand_name=name,
        description=desc,
        status='active'
    )
    db.session.add(brand)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"brand_create: {name}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Brand '{name}' created successfully.", "success")
    return redirect(url_for('brands.index'))

@brands_bp.route('/edit/<string:id>', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def edit(id):
    """
    Modifies brand fields.
    """
    brand = Brand.query.get_or_404(id)
    name = request.form.get('brand_name', '').strip()
    desc = request.form.get('description', '').strip()
    status = request.form.get('status', 'active').strip()
    
    if not name:
        flash("Brand name is required.", "danger")
        return redirect(url_for('brands.index'))
        
    existing = Brand.query.filter(Brand.brand_name.ilike(name), Brand.id != id).first()
    if existing:
        flash(f"A brand with name '{name}' already exists.", "danger")
        return redirect(url_for('brands.index'))
        
    brand.brand_name = name
    brand.description = desc
    brand.status = status
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"brand_update: {brand.brand_name}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Brand '{name}' updated successfully.", "success")
    return redirect(url_for('brands.index'))

@brands_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def delete(id):
    """
    Deletes brand if no products are associated with it.
    """
    brand = Brand.query.get_or_404(id)
    
    # Business Rule: Cannot delete brand if products exist
    associated_count = Product.query.filter_by(brand_id=id, deleted_at=None).count()
    if associated_count > 0:
        flash(f"Cannot delete brand '{brand.brand_name}' as it has {associated_count} associated product(s).", "danger")
        return redirect(url_for('brands.index'))
        
    db.session.delete(brand)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"brand_delete: {brand.brand_name}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Brand '{brand.brand_name}' has been deleted successfully.", "success")
    return redirect(url_for('brands.index'))
