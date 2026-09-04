"""
Inventory movements and valuation reports blueprint.
Handles stock adjustments and stock reports exports.
"""
from datetime import datetime
import csv
import io
import decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from openpyxl import Workbook

from database import db
from models.product import Product
from models.category import Category
from models.brand import Brand
from models.inventory_movement import InventoryMovement
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/history')
@login_required
def history():
    """
    Renders list of all inventory movement logs.
    """
    movements = InventoryMovement.query.order_by(InventoryMovement.created_at.desc()).all()
    return render_template('inventory/history.html', movements=movements)


@inventory_bp.route('/adjust', methods=['POST'])
@login_required
def adjust_stock():
    """
    Applies stock adjustments (Stock In, Stock Out, Adjustment, Damaged Stock, Returned Stock).
    Restricts Staff based on roles configuration (Staff can only adjust if permitted, Super Admin / Admin full access).
    """
    product_id = request.form.get('product_id', '').strip()
    qty_str = request.form.get('quantity', '').strip()
    adj_type = request.form.get('movement_type', '').strip() # Stock In, Stock Out, Adjustment
    remarks = request.form.get('remarks', '').strip()
    
    prod = Product.query.filter_by(id=product_id, deleted_at=None).first_or_404()
    
    # 1. Enforce quantity numeric formats
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError()
    except ValueError:
        flash("Adjustment quantity must be a positive integer.", "danger")
        return redirect(request.referrer or url_for('products.detail', id=product_id))
        
    prev_stock = prod.current_stock
    
    # 2. Apply stock adjustments
    if adj_type == 'Stock In' or adj_type == 'Return':
        new_stock = prev_stock + qty
    elif adj_type == 'Stock Out' or adj_type == 'Adjustment' or adj_type == 'Damaged':
        new_stock = prev_stock - qty
        # Business Rule: Stock cannot become negative!
        if new_stock < 0:
            flash(f"Cannot adjust stock. Product '{prod.product_name}' only has {prev_stock} units left.", "danger")
            return redirect(request.referrer or url_for('products.detail', id=product_id))
    else:
        flash("Invalid movement type selected.", "danger")
        return redirect(request.referrer or url_for('products.detail', id=product_id))
        
    prod.current_stock = new_stock
    
    # 3. Create movement log
    mov = InventoryMovement(
        product_id=prod.id,
        movement_type=adj_type,
        quantity=qty,
        previous_stock=prev_stock,
        new_stock=new_stock,
        remarks=remarks or f"Manual stock adjustment ({adj_type}).",
        created_by=current_user.id
    )
    db.session.add(mov)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"stock_adjust: {prod.product_code} ({adj_type} of {qty} items)",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f"Stock for '{prod.product_name}' adjusted successfully. New stock: {new_stock} {prod.unit}.", "success")
    return redirect(request.referrer or url_for('products.detail', id=product_id))


@inventory_bp.route('/reports')
@login_required
def reports():
    """
    Renders inventory reports valuation metrics dashboard.
    """
    products = Product.query.filter(Product.deleted_at == None).all()
    
    # Calculations
    total_items_count = len(products)
    low_stock_count = sum(1 for p in products if p.is_low_stock)
    out_of_stock_count = sum(1 for p in products if p.is_out_of_stock)
    
    # Total valuation (selling price * stock)
    total_selling_value = sum(p.stock_value for p in products)
    total_purchase_value = sum(float(p.purchase_price) * p.current_stock for p in products)
    
    return render_template(
        'inventory/reports.html',
        products=products,
        total_items_count=total_items_count,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        total_selling_value=total_selling_value,
        total_purchase_value=total_purchase_value
    )


@inventory_bp.route('/reports/export/<string:report_type>/<string:format_type>')
@login_required
@role_required(['Super Admin', 'Admin'])
def export_report(report_type, format_type):
    """
    Exports inventory reports as CSV/Excel files.
    """
    query = Product.query.filter(Product.deleted_at == None)
    
    if report_type == 'low_stock':
        # Filter products <= min_stock
        products = [p for p in query.all() if p.is_low_stock]
        title = "Low Stock Report"
    elif report_type == 'out_of_stock':
        products = query.filter(Product.current_stock <= 0).all()
        title = "Out of Stock Report"
    else:
        products = query.all()
        title = "Inventory Valuation Report"
        
    # Audit trail log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"inventory_report_export: {report_type} ({format_type})",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Product Code', 'Product Name', 'Barcode', 'Category', 'Selling Price', 'Current Stock', 'Unit', 'Total Valuation'])
        
        for p in products:
            writer.writerow([
                p.product_code, p.product_name, p.barcode, p.category.name,
                float(p.selling_price), p.current_stock, p.unit, p.stock_value
            ])
            
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
    elif format_type == 'excel':
        wb = Workbook()
        ws = wb.active
        ws.title = title
        
        # Headers
        ws.append(['Product Code', 'Product Name', 'Category', 'Brand', 'Purchase Price', 'Selling Price', 'Current Stock', 'Unit', 'Valuation'])
        
        for p in products:
            ws.append([
                p.product_code, p.product_name, p.category.name, p.brand.brand_name,
                float(p.purchase_price), float(p.selling_price), p.current_stock, p.unit, p.stock_value
            ])
            
        out_stream = io.BytesIO()
        wb.save(out_stream)
        out_stream.seek(0)
        return send_file(
            out_stream,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{report_type}_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )
        
    flash("Invalid report format requested.", "danger")
    return redirect(url_for('inventory.reports'))
