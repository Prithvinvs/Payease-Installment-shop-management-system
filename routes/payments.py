"""
Payments Web Blueprint.
Provides views to display payments list, collection wizards, receipts, and customer ledgers.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from database import db
from models.payment import Payment
from models.payment_receipt import PaymentReceipt
from models.customer import Customer
from models.customer_ledger import CustomerLedger
from models.instalment_plan import InstalmentPlan
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/')
@login_required
def index():
    """
    Lists payments history with filters.
    """
    filter_method = request.args.get('method', '').strip().lower()
    
    query = Payment.query
    if filter_method:
        query = query.filter(db.func.lower(Payment.payment_method) == filter_method)
        
    payments = query.order_by(Payment.payment_date.desc()).all()
    return render_template(
        'payments/list.html',
        payments=payments,
        current_method=filter_method
    )


@payments_bp.route('/collect', methods=['GET'])
@login_required
def collect_payment():
    """
    Renders payment entry collection page.
    Optionally pre-selects customer_id or plan_id.
    """
    pre_customer_id = request.args.get('customer_id', '').strip()
    pre_plan_id = request.args.get('plan_id', '').strip()
    
    customers = Customer.query.filter_by(deleted_at=None).all()
    
    selected_customer = None
    selected_plan = None
    if pre_customer_id:
        selected_customer = Customer.query.get(pre_customer_id)
    if pre_plan_id:
        selected_plan = InstalmentPlan.query.get(pre_plan_id)
        if selected_plan and not selected_customer:
            selected_customer = selected_plan.customer

    return render_template(
        'payments/entry.html',
        customers=customers,
        selected_customer=selected_customer,
        selected_plan=selected_plan
    )


@payments_bp.route('/receipt/<string:id>')
@login_required
def receipt(id):
    """
    Renders printed receipt page linked to payment event.
    """
    payment = Payment.query.get_or_404(id)
    return render_template('payments/receipt.html', payment=payment)


@payments_bp.route('/ledger/<string:customer_id>')
@login_required
def customer_ledger(customer_id):
    """
    Renders customer statement list showing running balances.
    """
    customer = Customer.query.get_or_404(customer_id)
    ledger_entries = CustomerLedger.query.filter_by(customer_id=customer.id).order_by(CustomerLedger.transaction_date.asc(), CustomerLedger.created_at.asc()).all()
    return render_template(
        'payments/ledger.html',
        customer=customer,
        ledger_entries=ledger_entries
    )
