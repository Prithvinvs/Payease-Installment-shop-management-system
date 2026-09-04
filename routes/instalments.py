"""
Instalment Management Web Blueprint.
Provides views to display instalment directories, progress trackers, and print schedules.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from database import db
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from models.customer import Customer
from models.sale import Sale
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

instalments_bp = Blueprint('instalments', __name__, url_prefix='/instalments')

@instalments_bp.route('/')
@login_required
def index():
    """
    Renders Instalment Plans index sheet.
    Supports status filters: active, overdue, completed, cancelled.
    """
    filter_status = request.args.get('status', '').strip().lower()
    
    query = InstalmentPlan.query
    if filter_status == 'active':
        query = query.filter(InstalmentPlan.status == 'active')
    elif filter_status == 'overdue':
        query = query.filter(InstalmentPlan.status == 'overdue')
    elif filter_status == 'completed':
        query = query.filter(InstalmentPlan.status == 'completed')
    elif filter_status == 'cancelled':
        query = query.filter(InstalmentPlan.status == 'cancelled')
        
    plans = query.order_by(InstalmentPlan.created_at.desc()).all()
    return render_template(
        'instalments/list.html',
        plans=plans,
        current_status=filter_status
    )


@instalments_bp.route('/<string:id>')
@login_required
def detail(id):
    """
    Renders complete instalment plan timeline details page.
    Shows summaries cards, schedule tables, and rescheduling trigger modal.
    """
    plan = InstalmentPlan.query.get_or_404(id)
    return render_template('instalments/detail.html', plan=plan)


@instalments_bp.route('/print/<string:id>')
@login_required
def print_schedule(id):
    """
    Renders print-friendly EMI instalment schedule ledger page.
    """
    plan = InstalmentPlan.query.get_or_404(id)
    
    # Audit log print action
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"instalment_print_schedule: {plan.plan_number}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    return render_template('instalments/print_schedule.html', plan=plan)
