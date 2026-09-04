"""
Payments REST JSON API Blueprint.
Manages recording collections, customer ledgers, and cash flow reports.
"""
from datetime import datetime, date, timedelta
import decimal
import uuid as uuid_pkg
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from database import db
from models.payment import Payment
from models.payment_receipt import PaymentReceipt
from models.customer import Customer
from models.customer_ledger import CustomerLedger
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from models.sale import Sale
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

payments_api_bp = Blueprint('payments_api', __name__, url_prefix='/api')

def generate_receipt_number():
    """
    Generates next sequential receipt code: RCT-2026-000001.
    """
    year = datetime.now().year
    prefix = f"RCT-{year}-"
    
    last_pay = Payment.query.filter(Payment.receipt_number.like(f"{prefix}%")).order_by(Payment.receipt_number.desc()).first()
    if not last_pay:
        return f"{prefix}000001"
        
    code = last_pay.receipt_number
    try:
        num = int(code.replace(prefix, ""))
        return f"{prefix}{num + 1:06d}"
    except ValueError:
        return f"{prefix}{uuid_pkg.uuid4().hex[:6].upper()}"

def payment_to_dict(p):
    return {
        'id': p.id,
        'receipt_number': p.receipt_number,
        'plan_id': p.plan_id,
        'schedule_id': p.schedule_id,
        'sale_id': p.sale_id,
        'invoice_number': p.invoice_number,
        'customer_id': p.customer_id,
        'customer_name': p.customer.full_name,
        'payment_amount': float(p.payment_amount),
        'payment_date': p.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
        'payment_type': p.payment_type,
        'payment_method': p.payment_method,
        'reference_number': p.reference_number,
        'bank_name': p.bank_name,
        'transaction_id': p.transaction_id,
        'remarks': p.remarks,
        'payment_status': p.payment_status,
        'received_by': p.received_by
    }

@payments_api_bp.route('/payments', methods=['GET'])
@login_required
def get_payments():
    payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return jsonify([payment_to_dict(p) for p in payments]), 200

@payments_api_bp.route('/payments/<string:id>', methods=['GET'])
@login_required
def get_payment(id):
    p = Payment.query.get(id)
    if not p:
        return jsonify({'error': 'Payment record not found'}), 404
    return jsonify(payment_to_dict(p)), 200

@payments_api_bp.route('/payments', methods=['POST'])
@login_required
def record_payment():
    """
    POST /api/payments
    Records a payment receipt, updates instalment plans/schedules,
    appends customer ledger line, and creates the payment receipt record.
    """
    data = request.json or {}
    customer_id = (data.get('customer_id') or '').strip()
    plan_id = (data.get('plan_id') or '').strip()
    schedule_id = (data.get('schedule_id') or '').strip()
    amount_val = data.get('amount', 0.0)
    pay_method = (data.get('payment_method') or 'Cash').strip()
    ref_no = (data.get('reference_number') or '').strip()
    bank_name = (data.get('bank_name') or '').strip()
    tx_id = (data.get('transaction_id') or '').strip()
    remarks = (data.get('remarks') or '').strip()
    
    # 1. Validations
    amount_raw = data.get('amount')
    if amount_raw is None or amount_raw == '':
        return jsonify({'error': 'Payment amount is required.'}), 400
    try:
        payment_dec = decimal.Decimal(str(amount_raw))
    except (decimal.InvalidOperation, ValueError, TypeError):
        return jsonify({'error': 'Invalid payment amount format.'}), 400
        
    if payment_dec <= 0:
        return jsonify({'error': 'Payment amount must be greater than zero.'}), 400
        
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404
        
    if tx_id:
        existing_tx = Payment.query.filter_by(transaction_id=tx_id).first()
        if existing_tx:
            return jsonify({'error': f"Duplicate payment detected. Transaction reference '{tx_id}' is already registered."}), 400

    plan = None
    if plan_id:
        plan = InstalmentPlan.query.get(plan_id)
        if not plan:
            return jsonify({'error': 'Instalment plan not found.'}), 404
        if plan.status == 'completed':
            return jsonify({'error': 'Cannot record payments against a completed plan.'}), 400
            
    # Calculate outstanding balance limit
    if plan:
        outstanding = plan.outstanding_amount
        if payment_dec > outstanding:
            return jsonify({'error': f"Payment amount of ₹{payment_dec:,.2f} exceeds plan remaining balance of ₹{outstanding:,.2f}."}), 400
            
    try:
        # Generate receipt code
        receipt_no = generate_receipt_number()
        
        # 2. Save Payment entry
        payment = Payment(
            receipt_number=receipt_no,
            plan_id=plan.id if plan else None,
            schedule_id=schedule_id if schedule_id else None,
            sale_id=plan.sale_id if plan else None,
            invoice_number=plan.invoice_number if (plan and plan.invoice_number) else 'DIRECT',
            customer_id=customer.id,
            payment_amount=payment_dec,
            payment_date=datetime.utcnow(),
            payment_type='EMI Payment' if plan else 'Direct Payment',
            payment_method=pay_method,
            reference_number=ref_no if ref_no else None,
            bank_name=bank_name if bank_name else None,
            transaction_id=tx_id if tx_id else None,
            remarks=remarks,
            received_by=current_user.id,
            payment_status='paid'
        )
        db.session.add(payment)
        db.session.flush() # Yields payment.id
        
        # 3. Process Instalments Schedules updates
        if plan:
            remaining_allocation = payment_dec
            
            # Case A: Paying a specific target schedule
            if schedule_id:
                target_sched = InstalmentSchedule.query.get(schedule_id)
                if target_sched and target_sched.payment_status != 'paid':
                    sched_bal = target_sched.balance
                    
                    if remaining_allocation >= sched_bal:
                        target_sched.paid_amount += sched_bal
                        target_sched.balance = decimal.Decimal(0.0)
                        target_sched.payment_status = 'paid'
                        target_sched.paid_date = datetime.utcnow()
                        target_sched.days_overdue = 0
                        remaining_allocation -= sched_bal
                    else:
                        target_sched.paid_amount += remaining_allocation
                        target_sched.balance -= remaining_allocation
                        target_sched.payment_status = 'partially_paid'
                        remaining_allocation = decimal.Decimal(0.0)
                        
            # Case B: Standard cascade or advance payments (exhausting excess values)
            if remaining_allocation > 0:
                unpaid_scheds = InstalmentSchedule.query.filter(
                    InstalmentSchedule.plan_id == plan.id,
                    InstalmentSchedule.payment_status != 'paid'
                ).order_by(InstalmentSchedule.instalment_number).all()
                
                for sched in unpaid_scheds:
                    if remaining_allocation <= 0:
                        break
                    sched_bal = sched.balance
                    
                    if remaining_allocation >= sched_bal:
                        sched.paid_amount += sched_bal
                        sched.balance = decimal.Decimal(0.0)
                        sched.payment_status = 'paid'
                        sched.paid_date = datetime.utcnow()
                        sched.days_overdue = 0
                        remaining_allocation -= sched_bal
                    else:
                        sched.paid_amount += remaining_allocation
                        sched.balance -= remaining_allocation
                        sched.payment_status = 'partially_paid'
                        remaining_allocation = decimal.Decimal(0.0)
                        
            # Update parent plan remaining balance
            plan.remaining_balance -= payment_dec
            
            # Recalculate plan overall status
            has_overdue = any(s.payment_status == 'overdue' for s in plan.schedules)
            all_paid = all(s.payment_status == 'paid' for s in plan.schedules)
            
            if all_paid or plan.remaining_balance <= 0:
                plan.status = 'completed'
            elif has_overdue:
                plan.status = 'overdue'
            else:
                plan.status = 'active'
                
        # 4. Update Customer Ledger
        last_ledger = CustomerLedger.query.filter_by(customer_id=customer.id).order_by(CustomerLedger.transaction_date.desc(), CustomerLedger.created_at.desc()).first()
        prev_bal = last_ledger.balance if last_ledger else decimal.Decimal(0.0)
        new_ledger_bal = prev_bal - payment_dec
        
        ledger = CustomerLedger(
            customer_id=customer.id,
            transaction_type='credit',
            reference_id=payment.id,
            description=f"EMI payment receipt: {receipt_no} against Invoice {plan.invoice_number}." if (plan and plan.invoice_number) else f"Direct payment receipt: {receipt_no}.",
            debit=decimal.Decimal(0.0),
            credit=payment_dec,
            balance=new_ledger_bal,
            transaction_date=datetime.utcnow()
        )
        db.session.add(ledger)
        
        # 5. Generate PaymentReceipt
        receipt = PaymentReceipt(
            receipt_number=receipt_no,
            payment_id=payment.id,
            invoice_number=plan.invoice_number if (plan and plan.invoice_number) else 'DIRECT',
            customer_id=customer.id,
            receipt_date=datetime.utcnow(),
            amount_received=payment_dec,
            payment_method=pay_method,
            generated_by=current_user.id
        )
        db.session.add(receipt)
        
        # 6. Audit Trail Logger
        audit = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action=f"payment_created: {receipt_no} (Amount: ₹{payment_dec})",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        db.session.commit()
        
        return jsonify({
            'message': f"Payment of ₹{payment_dec:,.2f} recorded successfully.",
            'receipt_number': receipt_no,
            'payment_id': payment.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Transaction failed: {str(e)}"}), 500


@payments_api_bp.route('/ledger/<string:customer_id>', methods=['GET'])
@login_required
def get_customer_ledger(customer_id):
    """
    GET /api/ledger/<customer_id>
    """
    entries = CustomerLedger.query.filter_by(customer_id=customer_id).order_by(CustomerLedger.transaction_date.asc(), CustomerLedger.created_at.asc()).all()
    return jsonify([{
        'id': e.id,
        'transaction_type': e.transaction_type,
        'reference_id': e.reference_id,
        'description': e.description,
        'debit': float(e.debit),
        'credit': float(e.credit),
        'balance': float(e.balance),
        'transaction_date': e.transaction_date.strftime('%Y-%m-%d %H:%M:%S')
    } for e in entries]), 200


@payments_api_bp.route('/payments/reports', methods=['GET'])
@login_required
@role_required(['Super Admin', 'Admin'])
def get_reports():
    """
    GET /api/payments/reports
    Compiles daily, weekly, and monthly collection metrics.
    """
    today = date.today()
    
    today_start = datetime.combine(today, datetime.min.time())
    week_start = today_start - timedelta(days=today.weekday())
    month_start = today_start.replace(day=1)
    
    # Collections sums
    today_coll = db.session.query(db.func.sum(Payment.payment_amount)).filter(Payment.payment_date >= today_start, Payment.payment_status == 'paid').scalar() or 0
    week_coll = db.session.query(db.func.sum(Payment.payment_amount)).filter(Payment.payment_date >= week_start, Payment.payment_status == 'paid').scalar() or 0
    month_coll = db.session.query(db.func.sum(Payment.payment_amount)).filter(Payment.payment_date >= month_start, Payment.payment_status == 'paid').scalar() or 0
    
    # Outstanding totals
    outstanding_total = 0.0
    active_plans = InstalmentPlan.query.filter(InstalmentPlan.status.in_(['active', 'overdue'])).all()
    for plan in active_plans:
        outstanding_total += float(plan.outstanding_amount)
        
    return jsonify({
        'today_collection': float(today_coll),
        'weekly_collection': float(week_coll),
        'monthly_collection': float(month_coll),
        'total_outstanding': outstanding_total
    }), 200
