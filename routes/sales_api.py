"""
Sales and Billing REST JSON API Blueprint.
Handles POS cart checkouts, invoice searches, and transaction cancellations.
"""
from datetime import datetime, date
import uuid as uuid_pkg
import decimal
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user

from database import db
from models.sale import Sale
from models.sale_item import SaleItem
from models.customer import Customer
from models.product import Product
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from models.payment import Payment
from models.customer_ledger import CustomerLedger
from models.payment_receipt import PaymentReceipt
from models.inventory_movement import InventoryMovement
from models.audit_log import AuditLog
from utils.auth_decorators import role_required

sales_api_bp = Blueprint('sales_api', __name__, url_prefix='/api')

def generate_invoice_number():
    """
    Generates next sequential invoice code: INV-2026-000001.
    """
    year = datetime.now().year
    prefix = f"INV-{year}-"
    
    last_sale = Sale.query.filter(Sale.invoice_number.like(f"{prefix}%")).order_by(Sale.invoice_number.desc()).first()
    if not last_sale:
        return f"{prefix}000001"
        
    code = last_sale.invoice_number
    try:
        num = int(code.replace(prefix, ""))
        return f"{prefix}{num + 1:06d}"
    except ValueError:
        return f"{prefix}{uuid_pkg.uuid4().hex[:6].upper()}"

def generate_plan_number():
    """
    Generates next sequential plan code: PLAN-2026-000001.
    """
    year = datetime.now().year
    prefix = f"PLAN-{year}-"
    
    last_plan = InstalmentPlan.query.filter(InstalmentPlan.plan_number.like(f"{prefix}%")).order_by(InstalmentPlan.plan_number.desc()).first()
    if not last_plan:
        return f"{prefix}000001"
        
    code = last_plan.plan_number
    try:
        num = int(code.replace(prefix, ""))
        return f"{prefix}{num + 1:06d}"
    except ValueError:
        return f"{prefix}{uuid_pkg.uuid4().hex[:6].upper()}"

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

def sale_to_dict(s):
    return {
        'id': s.id,
        'invoice_number': s.invoice_number,
        'customer_name': s.customer.full_name,
        'customer_code': s.customer.customer_code,
        'sale_date': s.sale_date.strftime('%Y-%m-%d %H:%M:%S'),
        'subtotal': float(s.subtotal),
        'discount_amount': float(s.discount_amount),
        'tax_amount': float(s.tax_amount),
        'grand_total': float(s.grand_total),
        'down_payment': float(s.down_payment),
        'remaining_balance': float(s.remaining_balance),
        'payment_status': s.payment_status,
        'sale_status': s.sale_status,
        'items': [{
            'product_name': item.product.product_name,
            'product_code': item.product.product_code,
            'quantity': item.quantity,
            'unit_price': float(item.unit_price),
            'discount': float(item.discount),
            'tax': float(item.tax),
            'total_price': float(item.total_price)
        } for item in s.items]
    }

@sales_api_bp.route('/sales', methods=['GET'])
@login_required
def get_sales():
    """
    GET /api/sales
    """
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return jsonify([sale_to_dict(s) for s in sales]), 200

@sales_api_bp.route('/sales/<string:id>', methods=['GET'])
@login_required
def get_sale(id):
    """
    GET /api/sales/<id>
    """
    s = Sale.query.get(id)
    if not s:
        return jsonify({'error': 'Invoice not found'}), 404
    return jsonify(sale_to_dict(s)), 200

@sales_api_bp.route('/sales', methods=['POST'])
@login_required
def create_sale():
    """
    POST /api/sales
    Processes cart checkouts, stock reductions, and creates instalment plans.
    """
    data = request.json or {}
    cust_id = data.get('customer_id', '').strip()
    cart = data.get('cart', [])
    down_payment_val = data.get('down_payment', 0.0)
    total_instalments = int(data.get('total_instalments', 0))
    due_day = int(data.get('due_day', 5))
    
    # 1. Validate Customer
    customer = Customer.query.filter_by(id=cust_id, deleted_at=None).first()
    if not customer:
        return jsonify({'error': 'Selected customer does not exist or has been deleted.'}), 400
        
    if not cart:
        return jsonify({'error': 'Shopping cart is empty.'}), 400
        
    # Open db transaction
    try:
        subtotal = decimal.Decimal(0.0)
        discount_amount = decimal.Decimal(0.0)
        tax_amount = decimal.Decimal(0.0)
        grand_total = decimal.Decimal(0.0)
        
        items_to_save = []
        stock_updates = []
        
        # 2. Loop over cart to compute line totals
        for cart_item in cart:
            prod_id = cart_item.get('product_id', '').strip()
            qty = int(cart_item.get('quantity', 1))
            disc_pct = decimal.Decimal(str(cart_item.get('discount', 0.0)))
            
            product = Product.query.filter_by(id=prod_id, deleted_at=None).first()
            if not product:
                return jsonify({'error': f"Product ID {prod_id} not found."}), 400
                
            # Business Rule: Prevent sale if stock is insufficient
            if product.current_stock < qty:
                return jsonify({'error': f"Insufficient stock for '{product.product_name}'. Available: {product.current_stock}."}), 400
                
            # Pricing Math (Inclusive GST Tax system)
            unit_price = product.selling_price
            disc_factor = (decimal.Decimal(100) - disc_pct) / decimal.Decimal(100)
            discounted_unit = unit_price * disc_factor
            
            line_total = discounted_unit * qty
            line_subtotal = line_total / (decimal.Decimal(1) + (product.gst_percentage / decimal.Decimal(100)))
            line_tax = line_total - line_subtotal
            line_discount = (unit_price - discounted_unit) * qty
            
            grand_total += line_total
            subtotal += line_subtotal
            tax_amount += line_tax
            discount_amount += line_discount
            
            # Prepare models
            sale_item = SaleItem(
                product_id=product.id,
                quantity=qty,
                unit_price=unit_price,
                discount=disc_pct,
                tax=product.gst_percentage,
                total_price=line_total
            )
            items_to_save.append(sale_item)
            stock_updates.append((product, qty))
            
        # Down payment validations
        down_payment = decimal.Decimal(str(down_payment_val))
        if down_payment > grand_total:
            return jsonify({'error': "Down payment amount cannot exceed the invoice grand total."}), 400
            
        remaining_balance = grand_total - down_payment
        
        # Generate Invoice Number
        invoice = generate_invoice_number()
        
        # Determine status
        pay_status = 'paid' if remaining_balance <= 0 else 'partial' if down_payment > 0 else 'pending'
        
        # 3. Create Sale parent record
        sale = Sale(
            invoice_number=invoice,
            customer_id=customer.id,
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            grand_total=grand_total,
            down_payment=down_payment,
            remaining_balance=remaining_balance,
            payment_status=pay_status,
            sale_status='completed',
            created_by=current_user.id
        )
        db.session.add(sale)
        db.session.flush() # Yields sale.id
        
        # 4. Associate Items and reduce stock
        for item in items_to_save:
            item.sale_id = sale.id
            db.session.add(item)
            
        for product, qty in stock_updates:
            prev_stock = product.current_stock
            product.current_stock -= qty
            
            # Create Movement log
            mov = InventoryMovement(
                product_id=product.id,
                movement_type='Sales',
                quantity=qty,
                previous_stock=prev_stock,
                new_stock=product.current_stock,
                remarks=f"POS Sale Invoice: {invoice}.",
                created_by=current_user.id
            )
            db.session.add(mov)
            
        # 5. Automatically create instalment plans if remaining balance exists
        if remaining_balance > 0 and total_instalments > 0:
            inst_amount = remaining_balance / decimal.Decimal(total_instalments)
            plan_num = generate_plan_number()
            
            from datetime import timedelta
            start_dt = datetime.utcnow()
            first_due = start_dt + timedelta(days=30)
            last_due = start_dt + timedelta(days=total_instalments * 30)
            
            plan = InstalmentPlan(
                plan_number=plan_num,
                sale_id=sale.id,
                customer_id=customer.id,
                invoice_number=invoice,
                total_amount=grand_total,
                down_payment=down_payment,
                remaining_balance=remaining_balance,
                number_of_instalments=total_instalments,
                monthly_emi=inst_amount,
                interest_rate=decimal.Decimal(0.0),
                processing_fee=decimal.Decimal(0.0),
                start_date=start_dt,
                first_due_date=first_due,
                last_due_date=last_due,
                status='active',
                created_by=current_user.id
            )
            db.session.add(plan)
            db.session.flush() # Yields plan.id
            
            # Create InstalmentSchedule breakdown rows
            for i in range(1, total_instalments + 1):
                due_dt = start_dt + timedelta(days=i * 30)
                sched = InstalmentSchedule(
                    plan_id=plan.id,
                    instalment_number=i,
                    due_date=due_dt,
                    amount=inst_amount,
                    balance=inst_amount,
                    payment_status='pending',
                    remarks=f"Generated instalment #{i}."
                )
                db.session.add(sched)
            
        # Log Customer Ledger Debit (for credit purchase)
        if remaining_balance > 0:
            initial_ledger = CustomerLedger(
                customer_id=customer.id,
                transaction_type='debit',
                reference_id=sale.id,
                description=f"Purchase invoice credit: {invoice}.",
                debit=remaining_balance,
                credit=decimal.Decimal(0.0),
                balance=decimal.Decimal(str(customer.outstanding_balance)) + remaining_balance,
                transaction_date=datetime.utcnow()
            )
            db.session.add(initial_ledger)

        # Save down payment entry in Payments table
        if down_payment > 0:
            rct_num = generate_receipt_number()
            payment = Payment(
                receipt_number=rct_num,
                plan_id=plan.id if (remaining_balance > 0 and total_instalments > 0) else None,
                sale_id=sale.id,
                invoice_number=invoice,
                customer_id=customer.id,
                payment_amount=down_payment,
                payment_date=datetime.utcnow(),
                payment_type='EMI Payment' if remaining_balance > 0 else 'Full Payment',
                payment_method='Cash',
                remarks='Down payment collected at checkout.',
                received_by=current_user.id,
                payment_status='paid'
            )
            db.session.add(payment)
            db.session.flush() # Yields payment.id
            
            # Create PaymentReceipt for down payment
            receipt = PaymentReceipt(
                receipt_number=rct_num,
                payment_id=payment.id,
                invoice_number=invoice,
                customer_id=customer.id,
                receipt_date=datetime.utcnow(),
                amount_received=down_payment,
                payment_method='Cash',
                generated_by=current_user.id
            )
            db.session.add(receipt)
            
        # Audit trail logger
        log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action=f"sale_create: {invoice} (Grand Total: ₹{grand_total})",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify(sale_to_dict(sale)), 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f"Transaction failed: {str(e)}"}), 500


@sales_api_bp.route('/sales/<string:id>', methods=['DELETE'])
@login_required
@role_required(['Super Admin', 'Admin'])
def cancel_sale(id):
    """
    DELETE /api/sales/<id>
    Cancels invoice, restores stock, and cancels instalment plan.
    """
    sale = Sale.query.get(id)
    if not sale:
        return jsonify({'error': 'Invoice not found'}), 404
        
    if sale.sale_status == 'cancelled':
        return jsonify({'error': 'Invoice is already cancelled.'}), 400
        
    try:
        # Restore product stock
        for item in sale.items:
            product = item.product
            prev_stock = product.current_stock
            product.current_stock += item.quantity
            
            # Log stock restoration movement
            mov = InventoryMovement(
                product_id=product.id,
                movement_type='Return',
                quantity=item.quantity,
                previous_stock=prev_stock,
                new_stock=product.current_stock,
                remarks=f"Invoice cancellation refund: {sale.invoice_number}.",
                created_by=current_user.id
            )
            db.session.add(mov)
            
        # Set invoice statuses to cancelled
        sale.sale_status = 'cancelled'
        sale.payment_status = 'pending' # Reset payment
        
        # Cancel linked instalment plan and schedules
        if sale.instalment_plan:
            sale.instalment_plan.status = 'cancelled'
            for sched in sale.instalment_plan.schedules:
                if sched.payment_status != 'paid':
                    sched.payment_status = 'cancelled'
            
        # Audit Log
        log = AuditLog(
            user_id=current_user.id,
            username=current_user.username,
            action=f"sale_cancel: {sale.invoice_number}",
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': f"Invoice {sale.invoice_number} cancelled successfully. Stocks restored."}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Cancellation failed: {str(e)}"}), 500


@sales_api_bp.route('/sales/search', methods=['GET'])
@login_required
def search_sales():
    """
    GET /api/sales/search?q=value
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([]), 200
        
    results = Sale.query.join(Customer).filter(
        (Sale.invoice_number.ilike(f"%{q}%")) |
        (Customer.full_name.ilike(f"%{q}%")) |
        (Customer.phone_number.ilike(f"%{q}%"))
    ).limit(20).all()
    
    return jsonify([sale_to_dict(s) for s in results]), 200
