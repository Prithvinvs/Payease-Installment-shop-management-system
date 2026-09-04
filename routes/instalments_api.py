"""
Instalments REST JSON API Blueprint.
Provides endpoints for rescheduling instalments, daily overdue scanners, and reports compilation.
"""
from datetime import datetime, timedelta, date
import decimal
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from database import db
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from models.customer import Customer
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

instalments_api_bp = Blueprint('instalments_api', __name__, url_prefix='/api')

def plan_to_dict(p):
    return {
        'id': p.id,
        'plan_number': p.plan_number,
        'invoice_number': p.invoice_number,
        'customer_name': p.customer.full_name,
        'customer_code': p.customer.customer_code,
        'total_amount': float(p.total_amount),
        'down_payment': float(p.down_payment),
        'remaining_balance': float(p.remaining_balance),
        'number_of_instalments': p.number_of_instalments,
        'monthly_emi': float(p.monthly_emi),
        'interest_rate': float(p.interest_rate),
        'processing_fee': float(p.processing_fee),
        'start_date': p.start_date.strftime('%Y-%m-%d'),
        'first_due_date': p.first_due_date.strftime('%Y-%m-%d'),
        'last_due_date': p.last_due_date.strftime('%Y-%m-%d'),
        'status': p.status,
        'paid_amount': float(p.paid_amount),
        'outstanding_amount': float(p.outstanding_amount),
        'schedules': [{
            'id': s.id,
            'instalment_number': s.instalment_number,
            'due_date': s.due_date.strftime('%Y-%m-%d'),
            'amount': float(s.amount),
            'paid_amount': float(s.paid_amount),
            'balance': float(s.balance),
            'payment_status': s.payment_status,
            'paid_date': s.paid_date.strftime('%Y-%m-%d') if s.paid_date else None,
            'days_overdue': s.days_overdue,
            'remarks': s.remarks
        } for s in p.schedules]
    }

@instalments_api_bp.route('/instalments', methods=['GET'])
@login_required
def get_plans():
    plans = InstalmentPlan.query.order_by(InstalmentPlan.created_at.desc()).all()
    return jsonify([plan_to_dict(p) for p in plans]), 200

@instalments_api_bp.route('/instalments/<string:id>', methods=['GET'])
@login_required
def get_plan(id):
    p = InstalmentPlan.query.get(id)
    if not p:
        return jsonify({'error': 'Instalment plan not found'}), 404
    return jsonify(plan_to_dict(p)), 200

@instalments_api_bp.route('/instalments/reschedule', methods=['POST'])
@login_required
@role_required(['Super Admin', 'Admin'])
def reschedule():
    """
    POST /api/instalments/reschedule
    Reschedules unpaid instalments starting from a target index.
    Admin/Super Admin only.
    """
    data = request.json or {}
    plan_id = data.get('plan_id', '').strip()
    from_number = int(data.get('reschedule_from_number', 1))
    new_due_str = data.get('new_due_date', '').strip()
    new_amount_val = data.get('new_amount', None)
    remarks_text = data.get('remarks', '').strip()
    
    plan = InstalmentPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Instalment plan not found'}), 404
        
    if plan.status == 'completed':
        return jsonify({'error': 'Cannot reschedule a completed instalment plan.'}), 400
        
    try:
        new_due_dt = datetime.strptime(new_due_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid new due date format. Expects YYYY-MM-DD.'}), 400
        
    # Find all schedules from_number onwards that are not paid
    scheds = InstalmentSchedule.query.filter(
        InstalmentSchedule.plan_id == plan.id,
        InstalmentSchedule.instalment_number >= from_number,
        InstalmentSchedule.payment_status != 'paid'
    ).order_by(InstalmentSchedule.instalment_number).all()
    
    if not scheds:
        return jsonify({'error': 'No unpaid instalments found to reschedule starting from this index.'}), 400
        
    try:
        # Keep track of previous configuration details for audit trail
        prev_emi = float(plan.monthly_emi)
        prev_last_due = plan.last_due_date.strftime('%Y-%m-%d')
        
        # 1. Loop and shift dates by 30-day increments
        for idx, sched in enumerate(scheds):
            shifted_due = new_due_dt + timedelta(days=idx * 30)
            
            # Save prior state
            prior_due = sched.due_date.strftime('%Y-%m-%d')
            prior_amt = float(sched.amount)
            
            sched.due_date = shifted_due
            if new_amount_val is not None:
                new_amt_dec = decimal.Decimal(str(new_amount_val))
                sched.amount = new_amt_dec
                sched.balance = new_amt_dec - sched.paid_amount
                
            # Recalculate status based on dates
            today = datetime.utcnow()
            if sched.balance <= 0:
                sched.payment_status = 'paid'
            elif shifted_due < today:
                sched.payment_status = 'overdue'
                sched.days_overdue = (today - shifted_due).days
            else:
                sched.payment_status = 'pending'
                sched.days_overdue = 0
                
            sched.remarks = remarks_text or f"Rescheduled from {prior_due}."
            
        # 2. Recompute parent plan metrics
        db.session.flush()
        
        # Last due date is updated to the due date of the final instalment
        final_sched = InstalmentSchedule.query.filter_by(plan_id=plan.id).order_by(InstalmentSchedule.instalment_number.desc()).first()
        if final_sched:
            plan.last_due_date = final_sched.due_date
            
        if new_amount_val is not None:
            plan.monthly_emi = decimal.Decimal(str(new_amount_val))
            
        # Re-evaluate parent plan status
        has_overdue = any(s.payment_status == 'overdue' for s in plan.schedules)
        all_paid = all(s.payment_status == 'paid' for s in plan.schedules)
        
        if all_paid:
            plan.status = 'completed'
        elif has_overdue:
            plan.status = 'overdue'
        else:
            plan.status = 'active'
            
        # 3. Save Auditor Change Logs
        log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action=f"instalment_reschedule: {plan.plan_number} (From Month: {from_number})",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': f"Plan {plan.plan_number} successfully rescheduled.",
            'new_monthly_emi': float(plan.monthly_emi),
            'new_last_due_date': plan.last_due_date.strftime('%Y-%m-%d')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Rescheduling failed: {str(e)}"}), 500


@instalments_api_bp.route('/instalments/overdue', methods=['GET'])
@login_required
def overdue_scanner():
    """
    GET /api/instalments/overdue
    Daily cron / scanning hook that flags unpaid schedules past due dates as overdue.
    """
    today = datetime.utcnow()
    updated_count = 0
    
    # Query all unpaid schedule records in pending status whose due dates are in the past
    overdue_scheds = InstalmentSchedule.query.filter(
        InstalmentSchedule.payment_status.in_(['pending', 'partially_paid']),
        InstalmentSchedule.due_date < today
    ).all()
    
    try:
        plans_to_update = set()
        for sched in overdue_scheds:
            sched.payment_status = 'overdue'
            sched.days_overdue = (today - sched.due_date).days
            plans_to_update.add(sched.plan)
            updated_count += 1
            
        # Update parent plans statuses
        for plan in plans_to_update:
            if plan.status == 'active':
                plan.status = 'overdue'
                
        if updated_count > 0:
            db.session.commit()
            
        return jsonify({
            'status': 'success',
            'scanned_at': today.strftime('%Y-%m-%d %H:%M:%S'),
            'marked_overdue_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Overdue scanning failed: {str(e)}"}), 500


@instalments_api_bp.route('/instalments/due-today', methods=['GET'])
@login_required
def due_today():
    """
    GET /api/instalments/due-today
    """
    today = date.today()
    results = InstalmentSchedule.query.filter(
        db.func.date(InstalmentSchedule.due_date) == today,
        InstalmentSchedule.payment_status != 'paid'
    ).all()
    
    return jsonify([{
        'plan_number': s.plan.plan_number,
        'customer_name': s.plan.customer.full_name,
        'instalment_number': s.instalment_number,
        'due_date': s.due_date.strftime('%Y-%m-%d'),
        'amount': float(s.amount),
        'balance': float(s.balance)
    } for s in results]), 200
