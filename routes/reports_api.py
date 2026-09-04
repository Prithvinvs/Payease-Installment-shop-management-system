"""
Reports & Business Analytics REST JSON API and Exporters Blueprint.
Provides database aggregations, forecasting calculations, and CSV/Excel downloads.
"""
from datetime import datetime, date, timedelta
import decimal
import csv
import io
from flask import Blueprint, jsonify, request, Response
from flask_login import login_required, current_user

from database import db
from models.sale import Sale
from models.sale_item import SaleItem
from models.customer import Customer
from models.product import Product
from models.payment import Payment
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from services.forecasting import forecast_monthly_revenue, forecast_monthly_collections, forecast_customer_growth
from utils.auth_decorators import role_required

reports_api_bp = Blueprint('reports_api', __name__, url_prefix='/api')

@reports_api_bp.route('/reports/dashboard', methods=['GET'])
@login_required
@role_required(['Super Admin', 'Admin'])
def get_dashboard_summary():
    """
    GET /api/reports/dashboard
    Compiles aggregate metrics and business linear forecasts.
    """
    total_sales = Sale.query.filter(Sale.sale_status != 'cancelled').count()
    total_customers = Customer.query.filter_by(deleted_at=None).count()
    active_customers = Customer.query.filter(Customer.deleted_at == None, Customer.status == 'active').count()
    
    # Financial metrics
    total_revenue = db.session.query(db.func.sum(Payment.payment_amount)).filter(Payment.payment_status == 'paid').scalar() or 0
    
    outstanding_total = 0.0
    active_plans = InstalmentPlan.query.filter(InstalmentPlan.status.in_(['active', 'overdue'])).all()
    for plan in active_plans:
        outstanding_total += float(plan.outstanding_amount)
        
    # Inventory metrics
    total_stock_value = 0.0
    prods = Product.query.filter(Product.deleted_at == None).all()
    for p in prods:
        total_stock_value += float(p.purchase_price) * p.current_stock
        
    low_stock_count = Product.query.filter(Product.current_stock <= Product.minimum_stock, Product.deleted_at == None).count()
    active_plans_count = InstalmentPlan.query.filter(InstalmentPlan.status.in_(['active', 'overdue'])).count()
    
    # Profit calculation: Sales selling_price - purchase_price
    total_profit = 0.0
    sales_items = SaleItem.query.join(Sale).filter(Sale.sale_status != 'cancelled').all()
    for item in sales_items:
        profit_per_unit = float(item.unit_price) - float(item.product.purchase_price)
        # Apply item discount if present
        disc = float(item.discount) / 100.0 if item.discount else 0.0
        unit_discount = float(item.unit_price) * disc
        total_profit += (profit_per_unit - unit_discount) * item.quantity

    # Run Forecasting Engine
    fc_rev = forecast_monthly_revenue()
    fc_coll = forecast_monthly_collections()
    fc_cust = forecast_customer_growth()

    return jsonify({
        'total_sales': total_sales,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'total_revenue': float(total_revenue),
        'total_outstanding': outstanding_total,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
        'active_instalment_plans': active_plans_count,
        'total_profit': total_profit,
        'forecast': {
            'expected_monthly_revenue': fc_rev,
            'expected_collections_next_30_days': fc_coll,
            'expected_customer_growth': fc_cust
        }
    }), 200


@reports_api_bp.route('/analytics', methods=['GET'])
@login_required
@role_required(['Super Admin', 'Admin'])
def get_charts():
    """
    GET /api/analytics
    Compiles Chart.js datasets.
    """
    today = date.today()
    
    # 1. Monthly Revenue Collections (6-Month history)
    rev_labels = []
    rev_values = []
    for i in range(5, -1, -1):
        m_start = (today - timedelta(days=i * 30)).replace(day=1)
        m_start_dt = datetime.combine(m_start, datetime.min.time())
        m_end_dt = (m_start_dt + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        rev_sum = db.session.query(db.func.sum(Payment.payment_amount)).filter(
            Payment.payment_date >= m_start_dt,
            Payment.payment_date <= m_end_dt,
            Payment.payment_status == 'paid'
        ).scalar() or 0
        
        rev_labels.append(m_start_dt.strftime('%b %Y'))
        rev_values.append(float(rev_sum))

    # 2. Top 5 Products sold by quantity
    top_products = db.session.query(
        Product.product_name,
        db.func.sum(SaleItem.quantity).label('qty')
    ).join(SaleItem, Product.id == SaleItem.product_id).join(Sale).filter(
        Sale.sale_status != 'cancelled'
    ).group_by(Product.product_name).order_by(db.desc('qty')).limit(5).all()
    
    prod_labels = [tp[0] for tp in top_products]
    prod_values = [int(tp[1]) for tp in top_products]

    # 3. Payment Methods Distribution
    pm_stats = db.session.query(
        Payment.payment_method,
        db.func.count(Payment.id).label('cnt')
    ).filter_by(payment_status='paid').group_by(Payment.payment_method).all()
    
    pm_labels = [pm[0] for pm in pm_stats]
    pm_values = [int(pm[1]) for pm in pm_stats]

    return jsonify({
        'revenue_trend': {
            'labels': rev_labels,
            'values': rev_values
        },
        'top_products': {
            'labels': prod_labels,
            'values': prod_values
        },
        'payment_methods': {
            'labels': pm_labels,
            'values': pm_values
        }
    }), 200


@reports_api_bp.route('/reports/export/csv', methods=['GET'])
@login_required
@role_required(['Super Admin', 'Admin'])
def export_csv():
    """
    GET /api/reports/export/csv?type={sales|payments|customers|products}
    Generates and streams a UTF-8 CSV attachment.
    """
    r_type = request.args.get('type', '').strip().lower()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    filename = f"report_{r_type}_{date.today().strftime('%Y%m%d')}.csv"
    
    if r_type == 'sales':
        writer.writerow(['Invoice Number', 'Customer Name', 'Sale Date', 'Subtotal', 'Tax Amount', 'Grand Total', 'Down Payment', 'Remaining Balance', 'Payment Status'])
        sales = Sale.query.filter(Sale.sale_status != 'cancelled').order_by(Sale.sale_date.desc()).all()
        for s in sales:
            writer.writerow([s.invoice_number, s.customer.full_name, s.sale_date.strftime('%Y-%m-%d %H:%M'), float(s.subtotal), float(s.tax_amount), float(s.grand_total), float(s.down_payment), float(s.remaining_balance), s.payment_status])
            
    elif r_type == 'payments':
        writer.writerow(['Receipt Number', 'Customer Name', 'Payment Date', 'Amount Paid', 'Payment Method', 'Transaction ID', 'Remarks'])
        payments = Payment.query.filter_by(payment_status='paid').order_by(Payment.payment_date.desc()).all()
        for p in payments:
            writer.writerow([p.receipt_number, p.customer.full_name, p.payment_date.strftime('%Y-%m-%d %H:%M'), float(p.payment_amount), p.payment_method, p.transaction_id or '', p.remarks or ''])
            
    elif r_type == 'customers':
        writer.writerow(['Customer Code', 'Full Name', 'Phone Number', 'Total Purchases', 'Total Paid', 'Outstanding Balance'])
        customers = Customer.query.filter_by(deleted_at=None).all()
        for c in customers:
            writer.writerow([c.customer_code, c.full_name, c.phone_number, float(c.total_purchases), float(c.total_payments), float(c.outstanding_balance)])
            
    elif r_type == 'products':
        writer.writerow(['Product Code', 'Product Name', 'Category', 'Brand', 'Purchase Price', 'Selling Price', 'Current Stock', 'Stock Value'])
        products = Product.query.filter(Product.deleted_at == None).all()
        for p in products:
            val = float(p.purchase_price) * p.current_stock
            writer.writerow([p.product_code, p.product_name, p.category.name if p.category else 'N/A', p.brand.brand_name if p.brand else 'N/A', float(p.purchase_price), float(p.selling_price), p.current_stock, val])
            
    else:
        return jsonify({'error': 'Invalid report type requested for CSV export.'}), 400
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


@reports_api_bp.route('/reports/export/excel', methods=['GET'])
@login_required
@role_required(['Super Admin', 'Admin'])
def export_excel():
    """
    GET /api/reports/export/excel?type={sales|payments|customers|products}
    Streams CSV format with Excel mimetype.
    """
    r_type = request.args.get('type', '').strip().lower()
    output = io.StringIO()
    writer = csv.writer(output)
    
    filename = f"report_{r_type}_{date.today().strftime('%Y%m%d')}.xls"
    
    if r_type == 'sales':
        writer.writerow(['Invoice Number', 'Customer Name', 'Sale Date', 'Subtotal', 'Tax Amount', 'Grand Total', 'Down Payment', 'Remaining Balance', 'Payment Status'])
        sales = Sale.query.filter(Sale.sale_status != 'cancelled').order_by(Sale.sale_date.desc()).all()
        for s in sales:
            writer.writerow([s.invoice_number, s.customer.full_name, s.sale_date.strftime('%Y-%m-%d %H:%M'), float(s.subtotal), float(s.tax_amount), float(s.grand_total), float(s.down_payment), float(s.remaining_balance), s.payment_status])
            
    elif r_type == 'payments':
        writer.writerow(['Receipt Number', 'Customer Name', 'Payment Date', 'Amount Paid', 'Payment Method', 'Transaction ID', 'Remarks'])
        payments = Payment.query.filter_by(payment_status='paid').order_by(Payment.payment_date.desc()).all()
        for p in payments:
            writer.writerow([p.receipt_number, p.customer.full_name, p.payment_date.strftime('%Y-%m-%d %H:%M'), float(p.payment_amount), p.payment_method, p.transaction_id or '', p.remarks or ''])
            
    elif r_type == 'customers':
        writer.writerow(['Customer Code', 'Full Name', 'Phone Number', 'Total Purchases', 'Total Paid', 'Outstanding Balance'])
        customers = Customer.query.filter_by(deleted_at=None).all()
        for c in customers:
            writer.writerow([c.customer_code, c.full_name, c.phone_number, float(c.total_purchases), float(c.total_payments), float(c.outstanding_balance)])
            
    elif r_type == 'products':
        writer.writerow(['Product Code', 'Product Name', 'Category', 'Brand', 'Purchase Price', 'Selling Price', 'Current Stock', 'Stock Value'])
        products = Product.query.filter(Product.deleted_at == None).all()
        for p in products:
            val = float(p.purchase_price) * p.current_stock
            writer.writerow([p.product_code, p.product_name, p.category.name if p.category else 'N/A', p.brand.brand_name if p.brand else 'N/A', float(p.purchase_price), float(p.selling_price), p.current_stock, val])
    else:
        return jsonify({'error': 'Invalid report type requested for Excel export.'}), 400

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="application/vnd.ms-excel",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )
