"""
Category management routes blueprint.
Handles CRUD actions for product categories.
"""
from datetime import datetime
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from database import db
from models.category import Category
from models.product import Product
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

def generate_category_code():
    """
    Calculates next sequence CATXXXX.
    """
    last_cat = Category.query.order_by(Category.category_code.desc()).first()
    if not last_cat:
        return "CAT0001"
    code = last_cat.category_code
    try:
        num = int(code.replace("CAT", ""))
        return f"CAT{num + 1:04d}"
    except ValueError:
        return f"CAT{uuid.uuid4().hex[:4].upper()}"

@categories_bp.route('/')
@login_required
def index():
    """
    Renders list of all product categories.
    """
    categories = Category.query.order_by(Category.category_code.desc()).all()
    return render_template('categories/list.html', categories=categories)

@categories_bp.route('/add', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def add():
    """
    Adds a new product category.
    """
    name = request.form.get('category_name', '').strip()
    desc = request.form.get('description', '').strip()
    
    if not name:
        flash("Category name is required.", "danger")
        return redirect(url_for('categories.index'))
        
    existing = Category.query.filter(Category.name.ilike(name)).first()
    if existing:
        flash(f"A category with name '{name}' already exists.", "danger")
        return redirect(url_for('categories.index'))
        
    code = generate_category_code()
    cat = Category(
        category_code=code,
        name=name,
        description=desc,
        status='active'
    )
    db.session.add(cat)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"category_create: {code} ({name})",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Category '{name}' created successfully with code {code}.", "success")
    return redirect(url_for('categories.index'))

@categories_bp.route('/edit/<string:id>', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def edit(id):
    """
    Modifies category fields.
    """
    cat = Category.query.get_or_404(id)
    name = request.form.get('category_name', '').strip()
    desc = request.form.get('description', '').strip()
    status = request.form.get('status', 'active').strip()
    
    if not name:
        flash("Category name is required.", "danger")
        return redirect(url_for('categories.index'))
        
    existing = Category.query.filter(Category.name.ilike(name), Category.id != id).first()
    if existing:
        flash(f"A category with name '{name}' already exists.", "danger")
        return redirect(url_for('categories.index'))
        
    cat.name = name
    cat.description = desc
    cat.status = status
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"category_update: {cat.category_code}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Category '{name}' updated successfully.", "success")
    return redirect(url_for('categories.index'))

@categories_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def delete(id):
    """
    Deletes category if no products are associated with it.
    """
    cat = Category.query.get_or_404(id)
    
    # Business Rule: Cannot delete category if products exist
    associated_count = Product.query.filter_by(category_id=id, deleted_at=None).count()
    if associated_count > 0:
        flash(f"Cannot delete category '{cat.name}' as it has {associated_count} associated product(s).", "danger")
        return redirect(url_for('categories.index'))
        
    db.session.delete(cat)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"category_delete: {cat.category_code}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Category '{cat.name}' has been deleted successfully.", "success")
    return redirect(url_for('categories.index'))
