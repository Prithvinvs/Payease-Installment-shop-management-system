"""
Sales and POS billing routes blueprint.
Handles POS checkout interface, history directory, details invoices, and printing.
"""
from datetime import datetime, date
import uuid
import decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from database import db
from models.sale import Sale
from models.sale_item import SaleItem
from models.customer import Customer
from models.product import Product
from models.instalment_plan import InstalmentPlan
from models.payment import Payment
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/')
@login_required
def index():
    """
    Renders Sales & Billing history list with filters.
    """
    filter_type = request.args.get('filter', '').strip().lower()
    search_q = request.args.get('search', '').strip()
    
    query = Sale.query
    
    # Apply date filters
    today = date.today()
    if filter_type == 'today':
        query = query.filter(db.func.date(Sale.sale_date) == today)
    elif filter_type == 'this_week':
        start_week = today - db.func.timedelta(days=today.weekday()) # approximate or timedelta
        # Simple date math fallback:
        start_date = datetime.now() - datetime.timedelta(days=7)
        query = query.filter(Sale.sale_date >= start_date)
    elif filter_type == 'this_month':
        query = query.filter(db.extract('month', Sale.sale_date) == today.month)
    elif filter_type == 'this_year':
        query = query.filter(db.extract('year', Sale.sale_date) == today.year)
        
    # Apply status filters
    if filter_type == 'paid':
        query = query.filter(Sale.payment_status == 'paid')
    elif filter_type == 'pending':
        query = query.filter(Sale.payment_status == 'pending')
    elif filter_type == 'cancelled':
        query = query.filter(Sale.sale_status == 'cancelled')
        
    sales = query.order_by(Sale.sale_date.desc()).all()
    
    return render_template(
        'sales/list.html',
        sales=sales,
        current_filter=filter_type
    )


@sales_bp.route('/pos')
@login_required
def pos():
    """
    Renders professional POS billing workspace screen.
    Loads customers list and active products stock list.
    """
    customers = Customer.query.filter_by(deleted_at=None, status='active').all()
    products = Product.query.filter_by(deleted_at=None, status='active').all()
    return render_template('sales/pos.html', customers=customers, products=products)


@sales_bp.route('/invoice/<string:id>')
@login_required
def invoice_detail(id):
    """
    Renders detailed invoice details dashboard.
    """
    sale = Sale.query.get_or_404(id)
    return render_template('sales/detail.html', sale=sale)


@sales_bp.route('/invoice/print/<string:id>')
@login_required
def invoice_print(id):
    """
    Renders print-optimized customer invoice layout.
    """
    sale = Sale.query.get_or_404(id)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"invoice_print: {sale.invoice_number}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    return render_template('sales/invoice_print.html', sale=sale, today=date.today())
