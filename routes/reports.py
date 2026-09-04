"""
Reports and Business Analytics Web Blueprint.
Handles view controllers for operational lists, BI dashboards, and financial summaries.
"""
from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from database import db
from models.sale import Sale
from models.customer import Customer
from models.product import Product
from models.payment import Payment
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from utils.auth_decorators import role_required

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@role_required(['Super Admin', 'Admin'])
def index():
    """
    Renders reports central BI dashboard.
    """
    return render_template('reports/dashboard.html')


@reports_bp.route('/sales')
@login_required
@role_required(['Super Admin', 'Admin'])
def sales():
    """
    Renders sales and employee performance sheets.
    """
    sales_list = Sale.query.filter(Sale.sale_status != 'cancelled').order_by(Sale.sale_date.desc()).all()
    return render_template('reports/sales.html', sales=sales_list)


@reports_bp.route('/customers')
@login_required
@role_required(['Super Admin', 'Admin'])
def customers():
    """
    Renders customer lifetimes values and outstanding metrics.
    """
    customers_list = Customer.query.filter_by(deleted_at=None).all()
    return render_template('reports/customers.html', customers=customers_list)


@reports_bp.route('/products')
@login_required
def products():
    """
    Renders inventory valuations and movement counts.
    All authenticated roles can access this operational report.
    """
    products_list = Product.query.filter(Product.deleted_at == None).all()
    return render_template('reports/products.html', products=products_list)


@reports_bp.route('/payments')
@login_required
def payments():
    """
    Renders collections history ledger list.
    All authenticated roles can access this operational report.
    """
    payments_list = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('reports/payments.html', payments=payments_list)


@reports_bp.route('/financial')
@login_required
@role_required(['Super Admin', 'Admin'])
def financial():
    """
    Renders gross profits, tax collections, and discounts statements.
    """
    return render_template('reports/financial.html')
