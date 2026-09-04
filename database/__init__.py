"""
Database module for the Instalment Shop Management System.
Initializes SQLAlchemy db object and manages database schema seeding.
"""
from datetime import datetime, timedelta
import decimal
import random
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from database.supabase_client import get_supabase_client

def init_db(app):
    """
    Initializes database application context with PostgreSQL/Supabase or SQLite fallback,
    registers all models, creates tables, and seeds default records.
    """
    if 'sqlalchemy' not in app.extensions:
        db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from models.role import Role
        from models.user import User
        from models.password_reset import PasswordResetToken
        from models.audit_log import AuditLog
        from models.category import Category
        from models.brand import Brand
        from models.product import Product
        from models.customer import Customer
        from models.sale import Sale
        from models.instalment_plan import InstalmentPlan
        from models.instalment_schedule import InstalmentSchedule
        from models.payment import Payment
        from models.customer_ledger import CustomerLedger
        from models.payment_receipt import PaymentReceipt
        from models.inventory_movement import InventoryMovement
        from models.sale_item import SaleItem
        from models.setting import Setting
        
        # Verify connection and create tables if needed
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in db_uri or 'supabase' in db_uri:
            app.logger.info("Connected to Supabase PostgreSQL Database (Managed via Supabase migrations).")
            return
        else:
            app.logger.info("Connecting to local SQLite Database...")
            db.create_all()
            
        # --- 1. Seed Roles ---
        default_roles = [
            {'id': 1, 'role_name': 'Super Admin', 'description': 'Full system control, user management, and configuration rights.'},
            {'id': 2, 'role_name': 'Admin', 'description': 'Shop owner permissions to manage customers, sales, inventory, and reports.'},
            {'id': 3, 'role_name': 'Staff', 'description': 'Front-counter staff permissions to record sales and collect payments.'}
        ]
        for r in default_roles:
            role = Role(id=r['id'], role_name=r['role_name'], description=r['description'])
            db.session.add(role)
        db.session.commit()
            
        # --- 2. Seed Default Users ---
        default_users = [
            {'username': 'superadmin', 'full_name': 'System Super Admin', 'email': 'superadmin@payease.com', 'phone': '+919999999999', 'password': 'Admin@123', 'role_id': 1, 'status': 'active'},
            {'username': 'admin', 'full_name': 'Shop Owner Admin', 'email': 'admin@payease.com', 'phone': '+918888888888', 'password': 'Admin@123', 'role_id': 2, 'status': 'active'},
            {'username': 'staff', 'full_name': 'Counter Staff Cashier', 'email': 'staff@payease.com', 'phone': '+917777777777', 'password': 'Admin@123', 'role_id': 3, 'status': 'active'}
        ]
        for u in default_users:
            user = User(username=u['username'], full_name=u['full_name'], email=u['email'], phone=u['phone'], role_id=u['role_id'], status=u['status'])
            user.set_password(u['password'])
            db.session.add(user)
        db.session.commit()
        
        admin_id = User.query.filter_by(username='superadmin').first().id
        
        # --- 2b. Seed Global Settings (Default values) ---
        default_settings = [
            ('shop_name', 'PayEase Store'),
            ('shop_address', 'MG Road, Bangalore, India'),
            ('shop_phone', '+91 98765 43210'),
            ('shop_email', 'info@payease.com'),
            ('gst_number', '29AAAAA1111A1Z1'),
            ('currency', 'INR'),
            ('timezone', 'Asia/Kolkata'),
            ('date_format', '%d-%b-%Y'),
            ('invoice_prefix', 'INV-'),
            ('receipt_prefix', 'RCT-'),
            ('backup_schedule', 'daily'),
            ('theme', 'light')
        ]
        for k, v in default_settings:
            sett = Setting(key=k, value=v)
            db.session.add(sett)
        db.session.commit()

        # --- 3. Seed 20 Product Categories ---
        categories = []
        for i in range(1, 21):
            cat = Category(
                category_code=f"CAT{i:04d}",
                name=f"Category {i}",
                description=f"Seeded Product Category description {i}.",
                status='active'
            )
            db.session.add(cat)
            categories.append(cat)
        db.session.commit()

        # --- 4. Seed 15 Product Brands ---
        brands = []
        for i in range(1, 16):
            brand = Brand(
                brand_name=f"Brand {i}",
                description=f"Seeded manufacturer brand description {i}.",
                status='active'
            )
            db.session.add(brand)
            brands.append(brand)
        db.session.commit()

        # --- 5. Seed 100 Customers ---
        customers = []
        today = datetime.utcnow()
        for i in range(1, 101):
            reg_date = today - timedelta(days=random.randint(30, 200))
            cust = Customer(
                customer_code=f"CUST{i:04d}",
                first_name=f"CustomerFirst{i}",
                last_name=f"CustomerLast{i}",
                full_name=f"CustomerFirst{i} CustomerLast{i}",
                email=f"customer{i}@payease.com",
                phone_number=f"+9198765{i:05d}",
                address_line1=f"Flat {i}, MG Road Residences",
                city='Bangalore',
                state='Karnataka',
                postal_code='560001',
                country='India',
                date_of_birth=datetime(1990, 1, 1).date() + timedelta(days=i * 20),
                gender='Male' if i % 2 == 0 else 'Female',
                created_at=reg_date,
                status='active'
            )
            db.session.add(cust)
            customers.append(cust)
        db.session.commit()

        # --- 6. Seed 50 Products ---
        products = []
        for i in range(1, 51):
            purchase_price = 10000.00 + (i * 1000)
            selling_price = purchase_price * 1.25
            prod = Product(
                product_code=f"PRD{i:04d}",
                barcode=f"BARCODE-{1000 + i}",
                qr_code=f"PRD{i:04d}",
                product_name=f"Product Name {i}",
                category_id=categories[i % len(categories)].id,
                brand_id=brands[i % len(brands)].id,
                description=f"Seeded premium product index {i}.",
                purchase_price=decimal.Decimal(str(purchase_price)),
                selling_price=decimal.Decimal(str(selling_price)),
                gst_percentage=decimal.Decimal('18.0'),
                discount_percentage=decimal.Decimal('0.0'),
                current_stock=100, # Large stock to support 300 checkouts
                minimum_stock=10,
                maximum_stock=500,
                unit='pcs',
                status='active',
                created_by=admin_id
            )
            db.session.add(prod)
            products.append(prod)
        db.session.commit()

        # Seed Initial Stock In Inventory Movements
        for p in products:
            m = InventoryMovement(
                product_id=p.id,
                movement_type='Stock In',
                quantity=100,
                previous_stock=0,
                new_stock=100,
                remarks='Opening stock load.',
                created_by=admin_id
            )
            db.session.add(m)
        db.session.commit()

        # --- 7. Seed 300 Sales, 300 Plans & 800 Payments ---
        # 300 sales checkouts spanning last 180 days
        for s_idx in range(1, 301):
            customer = customers[s_idx % len(customers)]
            product = products[s_idx % len(products)]
            
            sale_date = today - timedelta(days=180 - (s_idx * 0.5))
            invoice = f"INV-2026-{2000 + s_idx:06d}"
            
            total_val = product.selling_price
            down_pay = total_val * decimal.Decimal('0.20')
            rem_val = total_val - down_pay
            inst_amount = rem_val / decimal.Decimal('6') # 6 months EMIs
            
            subtotal = total_val / decimal.Decimal('1.18')
            tax_amount = total_val - subtotal
            
            sale = Sale(
                invoice_number=invoice,
                customer_id=customer.id,
                sale_date=sale_date,
                subtotal=subtotal,
                discount_amount=decimal.Decimal(0.0),
                tax_amount=tax_amount,
                grand_total=total_val,
                down_payment=down_pay,
                remaining_balance=rem_val,
                payment_status='partial',
                sale_status='completed',
                created_at=sale_date,
                created_by=admin_id
            )
            db.session.add(sale)
            db.session.flush()
            
            item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=1,
                unit_price=product.selling_price,
                discount=decimal.Decimal(0.0),
                tax=decimal.Decimal(18.0),
                total_price=product.selling_price
            )
            db.session.add(item)
            
            # Create active plan
            plan_num = f"PLAN-2026-{2000 + s_idx:06d}"
            plan = InstalmentPlan(
                plan_number=plan_num,
                sale_id=sale.id,
                customer_id=customer.id,
                invoice_number=invoice,
                total_amount=total_val,
                down_payment=down_pay,
                remaining_balance=rem_val,
                number_of_instalments=6,
                monthly_emi=inst_amount,
                interest_rate=decimal.Decimal('0.0'),
                processing_fee=decimal.Decimal('0.0'),
                start_date=sale_date,
                first_due_date=sale_date + timedelta(days=30),
                last_due_date=sale_date + timedelta(days=180),
                status='active',
                created_at=sale_date,
                created_by=admin_id
            )
            db.session.add(plan)
            db.session.flush()
            
            # Create schedules
            schedules = []
            for i in range(1, 7):
                due_dt = sale_date + timedelta(days=i * 30)
                sched = InstalmentSchedule(
                    plan_id=plan.id,
                    instalment_number=i,
                    due_date=due_dt,
                    amount=inst_amount,
                    paid_amount=decimal.Decimal('0.0'),
                    balance=inst_amount,
                    payment_status='pending',
                    remarks=f"Seeded instalment #{i}."
                )
                db.session.add(sched)
                schedules.append(sched)
            db.session.flush()
            
            # Debit Ledger Entry for Sale
            debit_ledger = CustomerLedger(
                customer_id=customer.id,
                transaction_type='debit',
                reference_id=sale.id,
                description=f"Purchase invoice credit: {invoice}.",
                debit=rem_val,
                credit=decimal.Decimal('0.0'),
                balance=rem_val,
                transaction_date=sale_date
            )
            db.session.add(debit_ledger)
            
            # Down payment creation (This accounts for the first 300 payments)
            dp_receipt_no = f"RCT-2026-{2000 + s_idx:06d}"
            dp_payment = Payment(
                receipt_number=dp_receipt_no,
                plan_id=plan.id,
                sale_id=sale.id,
                invoice_number=invoice,
                customer_id=customer.id,
                payment_amount=down_pay,
                payment_date=sale_date,
                payment_type='EMI Payment',
                payment_method='Cash',
                remarks='Down payment collected at checkout.',
                received_by=admin_id,
                payment_status='paid',
                created_at=sale_date
            )
            db.session.add(dp_payment)
            db.session.flush()
            
            dp_receipt = PaymentReceipt(
                receipt_number=dp_receipt_no,
                payment_id=dp_payment.id,
                invoice_number=invoice,
                customer_id=customer.id,
                receipt_date=sale_date,
                amount_received=down_pay,
                payment_method='Cash',
                generated_by=admin_id
            )
            db.session.add(dp_receipt)
            
            # Add monthly collections (First 250 plans get exactly 2 monthly payments = 500 payments)
            # Total payments generated = 300 (down payments) + 500 (collections) = 800 payments.
            if s_idx <= 250:
                running_ledger_balance = rem_val
                for p_idx in range(2):
                    sched_item = schedules[p_idx]
                    pay_date = sale_date + timedelta(days=(p_idx + 1) * 30)
                    
                    receipt_no = f"RCT-2026-{(2000 + s_idx) * 10 + p_idx + 1:06d}"
                    inst_payment = Payment(
                        receipt_number=receipt_no,
                        plan_id=plan.id,
                        schedule_id=sched_item.id,
                        sale_id=sale.id,
                        invoice_number=invoice,
                        customer_id=customer.id,
                        payment_amount=inst_amount,
                        payment_date=pay_date,
                        payment_type='EMI Payment',
                        payment_method='UPI',
                        remarks=f"EMI Payment instalment #{p_idx + 1} collected.",
                        received_by=admin_id,
                        payment_status='paid',
                        created_at=pay_date
                    )
                    db.session.add(inst_payment)
                    db.session.flush()
                    
                    inst_receipt = PaymentReceipt(
                        receipt_number=receipt_no,
                        payment_id=inst_payment.id,
                        invoice_number=invoice,
                        customer_id=customer.id,
                        receipt_date=pay_date,
                        amount_received=inst_amount,
                        payment_method='UPI',
                        generated_by=admin_id
                    )
                    db.session.add(inst_receipt)
                    
                    # Update Schedule row in DB
                    sched_item.paid_amount = inst_amount
                    sched_item.balance = decimal.Decimal('0.0')
                    sched_item.payment_status = 'paid'
                    sched_item.paid_date = pay_date
                    
                    # Credit Ledger
                    running_ledger_balance -= inst_amount
                    credit_ledger = CustomerLedger(
                        customer_id=customer.id,
                        transaction_type='credit',
                        reference_id=inst_payment.id,
                        description=f"EMI payment receipt: {receipt_no} against Plan {plan.plan_number}.",
                        debit=decimal.Decimal('0.0'),
                        credit=inst_amount,
                        balance=running_ledger_balance,
                        transaction_date=pay_date
                    )
                    db.session.add(credit_ledger)
                    
        db.session.commit()
