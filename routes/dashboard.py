"""
Dashboard routes blueprint.
Handles rendering of the main control panel, transaction grids, and global search.
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from models.customer import Customer
from models.product import Product
from models.sale import Sale
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from models.payment import Payment

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """
    Renders the administrative dashboard template skeleton.
    Loads recent database lists directly for immediate view display.
    """
    # 1. Recent Sales (Latest 10 records)
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(10).all()
    
    # 2. Recent Payments (Latest 10 payments)
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(10).all()
    
    # 3. Low Stock Products (Highlighting stock below minimum level)
    low_stock_products = Product.query.filter(Product.current_stock <= Product.minimum_stock, Product.deleted_at == None).all()
    
    # 4. Recent Customers (Latest 10 customers)
    recent_customers = Customer.query.order_by(Customer.created_at.desc()).limit(10).all()
    
    # 5. Upcoming Due Payments (Calculated dynamically from active plans schedules)
    today = datetime.utcnow()
    upcoming_dues = []
    
    thirty_days_later = today + timedelta(days=30)
    active_schedules = InstalmentSchedule.query.filter(
        InstalmentSchedule.payment_status.in_(['pending', 'overdue']),
        InstalmentSchedule.due_date <= thirty_days_later
    ).order_by(InstalmentSchedule.due_date).all()
    
    for item in active_schedules:
        due_dt = item.due_date.replace(tzinfo=None) if hasattr(item.due_date, 'tzinfo') and item.due_date.tzinfo else item.due_date
        days_rem = (due_dt - today).days
        if item.payment_status == 'overdue':
            priority_color = 'danger'
            priority_label = 'Overdue'
        elif days_rem <= 0:
            priority_color = 'danger'
            priority_label = 'Due Today'
        elif days_rem < 3:
            priority_color = 'warning'
            priority_label = f"{days_rem} days left"
        else:
            priority_color = 'success'
            priority_label = f"{days_rem} days left"
            
        upcoming_dues.append({
            'customer': item.plan.customer.full_name,
            'invoice': item.plan.invoice_number,
            'due_date': item.due_date.strftime('%Y-%m-%d'),
            'amount': item.amount,
            'days_remaining': days_rem,
            'priority': priority_color,
            'priority_label': priority_label
        })
        
    # Sort upcoming dues closest first
    upcoming_dues.sort(key=lambda x: x['days_remaining'])
    upcoming_dues_list = upcoming_dues[:10]
    
    return render_template(
        'dashboard.html',
        recent_sales=recent_sales,
        recent_payments=recent_payments,
        low_stock_products=low_stock_products,
        recent_customers=recent_customers,
        upcoming_dues=upcoming_dues_list
    )


@dashboard_bp.route('/search')
@login_required
def search():
    """
    Global search route querying customers, products, sales, and payments.
    """
    search_query = request.args.get('q', '').strip()
    results = {
        'customers': [],
        'products': [],
        'sales': [],
        'payments': []
    }
    
    if search_query:
        # Search Customers
        results['customers'] = Customer.query.filter(
            (Customer.full_name.ilike(f"%{search_query}%")) |
            (Customer.email.ilike(f"%{search_query}%")) |
            (Customer.phone.ilike(f"%{search_query}%"))
        ).limit(10).all()
        
        # Search Products
        results['products'] = Product.query.filter(
            (Product.name.ilike(f"%{search_query}%")) |
            (Product.sku.ilike(f"%{search_query}%"))
        ).limit(10).all()
        
        # Search Sales / Invoices
        results['sales'] = Sale.query.filter(
            Sale.invoice_number.ilike(f"%{search_query}%")
        ).limit(10).all()
        
        # Search Payments
        results['payments'] = Payment.query.join(Customer).filter(
            (Customer.full_name.ilike(f"%{search_query}%")) |
            (Payment.status.ilike(f"%{search_query}%"))
        ).limit(10).all()
        
    return render_template('search.html', query=search_query, results=results)
