"""
Database Seeding Script for Instalment Shop Management System.
Populates the database with rich, realistic fake data including categories, brands,
products, customers, sales, instalment plans, schedules, payments, receipts, and ledgers.
"""

import sys
import os
import random
import decimal
from datetime import datetime, timedelta

# Add parent directory to path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database import db
from models.role import Role
from models.user import User
from models.category import Category
from models.brand import Brand
from models.product import Product
from models.customer import Customer
from models.sale import Sale
from models.sale_item import SaleItem
from models.instalment_plan import InstalmentPlan
from models.instalment_schedule import InstalmentSchedule
from models.payment import Payment
from models.payment_receipt import PaymentReceipt
from models.customer_ledger import CustomerLedger
from models.inventory_movement import InventoryMovement
from models.setting import Setting
from models.audit_log import AuditLog
from sqlalchemy import text

def seed_fake_data():
    app = create_app()
    with app.app_context():
        print("Starting Database Fake Data Injection...")
        
        # 1. Seed Roles
        roles_data = [
            (1, 'Super Admin', 'Full system control, user management, and configuration rights.', '{"all": true}'),
            (2, 'Admin', 'Shop owner permissions to manage customers, sales, inventory, and reports.', '{"manage_shop": true}'),
            (3, 'Manager', 'Store manager permissions to approve credits and monitor operations.', '{"manage_inventory": true, "manage_sales": true}'),
            (4, 'Staff', 'Front-counter staff permissions to record sales and collect payments.', '{"record_sales": true, "collect_payments": true}')
        ]
        
        for r_id, name, desc, perms in roles_data:
            existing = Role.query.get(r_id)
            if not existing:
                role = Role(id=r_id, role_name=name, description=desc)
                db.session.add(role)
        db.session.commit()
        print("  - Roles checked/seeded.")

        # 2. Seed Users
        users_data = [
            (1, 'superadmin', 'System Super Admin', 'superadmin@payease.com', '+919999999999', 'Admin@123', 1),
            (2, 'admin', 'Shop Owner Admin', 'admin@payease.com', '+918888888888', 'Admin@123', 2),
            (3, 'manager', 'Store Manager John', 'manager@payease.com', '+917777777700', 'Admin@123', 3),
            (4, 'staff', 'Cashier Ramesh', 'staff@payease.com', '+917777777777', 'Admin@123', 4),
            (5, 'cashier2', 'Cashier Priya Sharma', 'priya@payease.com', '+915555555555', 'Admin@123', 4)
        ]
        
        seeded_users = []
        for u_id, uname, fname, email, phone, pwd, r_id in users_data:
            user = User.query.filter((User.username == uname) | (User.phone == phone) | (User.email == email)).first()
            if not user:
                user = User(
                    username=uname,
                    full_name=fname,
                    email=email,
                    phone=phone,
                    role_id=r_id,
                    status='active'
                )
                user.set_password(pwd)
                db.session.add(user)
                db.session.flush()
            seeded_users.append(user)
        db.session.commit()
        print(f"  - {len(seeded_users)} System Users ready.")
        admin_user_id = seeded_users[1].id

        # 3. Seed Global Settings
        settings_data = [
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
        for key, value in settings_data:
            setting = Setting.query.filter_by(key=key).first()
            if not setting:
                db.session.add(Setting(key=key, value=value))
        db.session.commit()
        print("  - Global Settings verified.")

        # 4. Seed Product Categories
        categories_raw = [
            ("CAT-MOB", "Smartphones & Mobiles", "Latest Android and iOS smartphones"),
            ("CAT-LAP", "Laptops & Computers", "Gaming, office, and ultra-portable laptops"),
            ("CAT-TV", "Smart TVs & Home Theatre", "4K OLED, QLED TVs, and soundbars"),
            ("CAT-REF", "Refrigerators", "Single door, double door, and side-by-side fridges"),
            ("CAT-WM", "Washing Machines", "Front load and top load washing machines"),
            ("CAT-AC", "Air Conditioners", "Inverter split ACs and window AC units"),
            ("CAT-KA", "Kitchen Appliances", "Microwaves, water purifiers, and mixers"),
            ("CAT-FUR", "Furniture & Comfort", "Sofas, recliners, and queen size beds"),
            ("CAT-EV", "Electric Scooters", "Eco-friendly electric two-wheelers"),
            ("CAT-ACC", "Audio & Wearables", "Wireless earbuds, smartwatches, and headphones")
        ]
        
        category_objs = {}
        for code, name, desc in categories_raw:
            cat = Category.query.filter_by(category_code=code).first()
            if not cat:
                cat = Category(category_code=code, name=name, description=desc, status='active')
                db.session.add(cat)
                db.session.flush()
            category_objs[code] = cat
        db.session.commit()
        print(f"  - {len(category_objs)} Categories ready.")

        # 5. Seed Brands
        brands_raw = [
            ("Apple", "Premium iPhones, MacBooks, and iPads"),
            ("Samsung", "Global leader in Mobiles, TVs, and Appliances"),
            ("Sony", "Premium Audio, Bravia TVs, and Playstation"),
            ("LG", "Innovators in OLED TVs, Refrigerators, and Washing Machines"),
            ("Dell", "High performance XPS and Inspiron Laptops"),
            ("HP", "HP Pavilion and Spectre Laptops"),
            ("Xiaomi", "Value-for-money Redmi smartphones and Smart TVs"),
            ("OnePlus", "Never Settle Flagship Smartphones"),
            ("Whirlpool", "Home and Kitchen Appliances"),
            ("Voltas", "India's No. 1 Air Conditioner brand"),
            ("Godrej", "Refrigerators, Safes, and Home Appliances"),
            ("Bajaj", "Electricals and Kitchen Appliances"),
            ("Ather", "Smart Electric Scooters"),
            ("boAt", "Popular Indian Audio & Wearables brand")
        ]

        brand_objs = {}
        for b_name, b_desc in brands_raw:
            brand = Brand.query.filter_by(brand_name=b_name).first()
            if not brand:
                brand = Brand(brand_name=b_name, description=b_desc, status='active')
                db.session.add(brand)
                db.session.flush()
            brand_objs[b_name] = brand
        db.session.commit()
        print(f"  - {len(brand_objs)} Brands ready.")

        # 6. Seed Products
        products_raw = [
            ("PRD-1001", "890123401001", "iPhone 15 Pro 128GB", "CAT-MOB", "Apple", 125000.00, 134900.00, 45),
            ("PRD-1002", "890123401002", "iPhone 14 128GB StarLight", "CAT-MOB", "Apple", 58000.00, 64900.00, 30),
            ("PRD-1003", "890123401003", "Samsung Galaxy S24 Ultra 5G", "CAT-MOB", "Samsung", 118000.00, 129999.00, 25),
            ("PRD-1004", "890123401004", "Samsung Galaxy A55 5G", "CAT-MOB", "Samsung", 32000.00, 39999.00, 60),
            ("PRD-1005", "890123401005", "OnePlus 12 256GB Silky Black", "CAT-MOB", "OnePlus", 54000.00, 64999.00, 35),
            ("PRD-1006", "890123401006", "Redmi Note 13 Pro+ 5G", "CAT-MOB", "Xiaomi", 26000.00, 31999.00, 50),
            ("PRD-1007", "890123401007", "Apple MacBook Air M2 13.6-inch", "CAT-LAP", "Apple", 89000.00, 99900.00, 20),
            ("PRD-1008", "890123401008", "Dell XPS 13 Intel Core i7", "CAT-LAP", "Dell", 115000.00, 135000.00, 15),
            ("PRD-1009", "890123401009", "HP Pavilion 15 Ryzen 7", "CAT-LAP", "HP", 56000.00, 67990.00, 40),
            ("PRD-1010", "890123401010", "Sony Bravia 55-inch 4K Ultra HD OLED", "CAT-TV", "Sony", 120000.00, 139900.00, 18),
            ("PRD-1011", "890123401011", "LG 43-inch 4K Smart LED TV", "CAT-TV", "LG", 28000.00, 34990.00, 35),
            ("PRD-1012", "890123401012", "Xiaomi 50-inch X Pro 4K TV", "CAT-TV", "Xiaomi", 30000.00, 36999.00, 40),
            ("PRD-1013", "890123401013", "LG 260L Double Door Refrigerator", "CAT-REF", "LG", 22000.00, 27490.00, 25),
            ("PRD-1014", "890123401014", "Samsung 324L Convertible 5in1 Fridge", "CAT-REF", "Samsung", 31000.00, 38990.00, 20),
            ("PRD-1015", "890123401015", "Whirlpool 240L Multi-Door Fridge", "CAT-REF", "Whirlpool", 24000.00, 29990.00, 30),
            ("PRD-1016", "890123401016", "Godrej 190L Single Door Refrigerator", "CAT-REF", "Godrej", 14000.00, 17490.00, 40),
            ("PRD-1017", "890123401017", "LG 8.0 Kg Front Load Washing Machine", "CAT-WM", "LG", 32000.00, 38990.00, 22),
            ("PRD-1018", "890123401018", "Samsung 7.0 Kg Top Load Washer", "CAT-WM", "Samsung", 16500.00, 19990.00, 35),
            ("PRD-1019", "890123401019", "Voltas 1.5 Ton 5 Star Inverter Split AC", "CAT-AC", "Voltas", 34000.00, 41990.00, 30),
            ("PRD-1020", "890123401020", "LG 1.5 Ton 3 Star Dual Inverter AC", "CAT-AC", "LG", 33000.00, 39490.00, 28),
            ("PRD-1021", "890123401021", "Bajaj 20L Grill Microwave Oven", "CAT-KA", "Bajaj", 5500.00, 7290.00, 50),
            ("PRD-1022", "890123401022", "Whirlpool 20L Solo Microwave", "CAT-KA", "Whirlpool", 4800.00, 6190.00, 45),
            ("PRD-1023", "890123401023", "Ather 450X Gen 3 Electric Scooter", "CAT-EV", "Ather", 125000.00, 144999.00, 12),
            ("PRD-1024", "890123401024", "Sony WH-1000XM5 Wireless Headphones", "CAT-ACC", "Sony", 24000.00, 29990.00, 40),
            ("PRD-1025", "890123401025", "boAt Airdopes 141 ANC Earbuds", "CAT-ACC", "boAt", 1200.00, 1699.00, 100)
        ]

        product_objs = []
        for pcode, barcode, pname, cat_code, bname, p_price, s_price, stock in products_raw:
            prod = Product.query.filter_by(product_code=pcode).first()
            if not prod:
                prod = Product(
                    product_code=pcode,
                    barcode=barcode,
                    qr_code=pcode,
                    product_name=pname,
                    category_id=category_objs[cat_code].id,
                    brand_id=brand_objs[bname].id,
                    description=f"{pname} with official manufacturer warranty and instalment eligibility.",
                    purchase_price=decimal.Decimal(str(p_price)),
                    selling_price=decimal.Decimal(str(s_price)),
                    gst_percentage=decimal.Decimal('18.0'),
                    discount_percentage=decimal.Decimal('0.0'),
                    current_stock=stock,
                    minimum_stock=5,
                    maximum_stock=200,
                    unit='pcs',
                    status='active',
                    created_by=admin_user_id
                )
                db.session.add(prod)
                db.session.flush()
                
                # Stock In movement record
                mv = InventoryMovement(
                    product_id=prod.id,
                    movement_type='Stock In',
                    quantity=stock + 20, # Initial shipment
                    previous_stock=0,
                    new_stock=stock + 20,
                    remarks='Initial stock warehouse load.',
                    created_by=admin_user_id
                )
                db.session.add(mv)
            product_objs.append(prod)
        db.session.commit()
        print(f"  - {len(product_objs)} Products & Inventory Movements ready.")

        # 7. Seed Customers
        customers_raw = [
            ("CUST-0001", "Rajesh", "Kumar", "rajesh.kumar@gmail.com", "+919876543201", "M-12, Indiranagar 100ft Road", "Bangalore", "Karnataka", "560038", "1988-05-14", "Male", "Software Engineer", "452189023412"),
            ("CUST-0002", "Priya", "Sharma", "priya.sharma@yahoo.com", "+919876543202", "Flat 402, Green Glen Layout", "Bangalore", "Karnataka", "560103", "1992-09-21", "Female", "Bank Manager", "893412095678"),
            ("CUST-0003", "Amit", "Verma", "amit.verma@outlook.com", "+919876543203", "Plot 45, Jubilee Hills Phase 2", "Hyderabad", "Telangana", "500033", "1985-12-03", "Male", "Business Owner", "671234890123"),
            ("CUST-0004", "Sneha", "Reddy", "sneha.reddy@gmail.com", "+919876543204", "12/A, Banjara Hills Road No 12", "Hyderabad", "Telangana", "500034", "1995-04-18", "Female", "Architect", "349012785634"),
            ("CUST-0005", "Vikram", "Singh", "vikram.singh@gmail.com", "+919876543205", "78, Koregaon Park Lane 5", "Pune", "Maharashtra", "411001", "1990-07-29", "Male", "Consultant", "901234567812"),
            ("CUST-0006", "Kavita", "Nair", "kavita.nair@hotmail.com", "+919876543206", "201, Hiranandani Gardens", "Mumbai", "Maharashtra", "400076", "1991-11-11", "Female", "Doctor", "123456789045"),
            ("CUST-0007", "Ananya", "Iyer", "ananya.iyer@gmail.com", "+919876543207", "56, T. Nagar Main Road", "Chennai", "Tamil Nadu", "600017", "1994-03-25", "Female", "Data Analyst", "567890123456"),
            ("CUST-0008", "Suresh", "Patel", "suresh.patel@gmail.com", "+919876543208", "102, CG Road Complex", "Ahmedabad", "Gujarat", "380009", "1983-08-08", "Male", "Trader", "789012345678"),
            ("CUST-0009", "Deepak", "Chawla", "deepak.c@gmail.com", "+919876543209", "B-40, Greater Kailash 1", "New Delhi", "Delhi", "110048", "1987-01-30", "Male", "Civil Servant", "234567890123"),
            ("CUST-0010", "Meera", "Deshmukh", "meera.d@gmail.com", "+919876543210", "15, FC Road Shivajinagar", "Pune", "Maharashtra", "411005", "1996-10-05", "Female", "Teacher", "890123456789"),
            ("CUST-0011", "Rohan", "Gupta", "rohan.gupta@gmail.com", "+919876543211", "Sector 15, Vasundhara", "Ghaziabad", "Uttar Pradesh", "201012", "1993-06-12", "Male", "HR Specialist", "345678901234"),
            ("CUST-0012", "Pooja", "Joshi", "pooja.joshi@gmail.com", "+919876543212", "44, C-Scheme Road", "Jaipur", "Rajasthan", "302001", "1997-02-14", "Female", "Designer", "901234567890"),
            ("CUST-0013", "Arjun", "Mehta", "arjun.m@gmail.com", "+919876543213", "303, Salt Lake Sector 5", "Kolkata", "West Bengal", "700091", "1989-09-09", "Male", "Project Manager", "456789012345"),
            ("CUST-0014", "Divya", "Kulkarni", "divya.k@gmail.com", "+919876543214", "88, MG Road Camp", "Belgaum", "Karnataka", "590001", "1995-12-28", "Female", "Pharmacist", "012345678901"),
            ("CUST-0015", "Karthik", "Raman", "karthik.r@gmail.com", "+919876543215", "12, Adyar Avenue", "Chennai", "Tamil Nadu", "600020", "1991-04-04", "Male", "Systems Engineer", "678901234567")
        ]

        customer_objs = []
        today = datetime.utcnow()
        for ccode, fname, lname, email, phone, addr, city, state, pcode, dob_str, gender, occ, aadhaar in customers_raw:
            cust = Customer.query.filter_by(customer_code=ccode).first()
            if not cust:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                created_dt = today - timedelta(days=random.randint(90, 200))
                cust = Customer(
                    customer_code=ccode,
                    first_name=fname,
                    last_name=lname,
                    full_name=f"{fname} {lname}",
                    email=email,
                    phone_number=phone,
                    address_line1=addr,
                    city=city,
                    state=state,
                    postal_code=pcode,
                    country='India',
                    date_of_birth=dob,
                    gender=gender,
                    occupation=occ,
                    aadhaar_number=aadhaar,
                    status='active',
                    created_at=created_dt,
                    created_by=admin_user_id
                )
                db.session.add(cust)
                db.session.flush()
            customer_objs.append(cust)
        db.session.commit()
        print(f"  - {len(customer_objs)} Customers ready.")

        # 8. Seed Sales, Instalment Plans, Schedules, Payments, Receipts, and Ledgers
        # Create 30 realistic instalment credit sales across past 180 days
        print("  - Injecting Sales, Instalment Plans, Schedules & Payments...")

        payment_methods = ['Cash', 'UPI', 'Credit Card', 'Net Banking']
        
        # We will create 30 sales with different scenarios:
        # - Sales 1-12: Completed plans (all EMIs paid on time)
        # - Sales 13-24: Active plans (some EMIs paid up to date, remaining pending)
        # - Sales 25-30: Overdue plans (some EMIs missed/unpaid beyond due date)

        sales_created = 0
        plans_created = 0
        payments_created = 0

        for i in range(1, 31):
            inv_no = f"INV-2026-{1000 + i:06d}"
            existing_sale = Sale.query.filter_by(invoice_number=inv_no).first()
            if existing_sale:
                continue

            customer = customer_objs[(i - 1) % len(customer_objs)]
            product = product_objs[(i - 1) % len(product_objs)]

            # Determine sale date (spanning past 180 days)
            days_ago = 180 - (i * 5)
            sale_dt = today - timedelta(days=days_ago)

            unit_price = product.selling_price
            qty = 1
            tax_rate = decimal.Decimal('18.0')
            
            subtotal = unit_price / (decimal.Decimal('1.0') + (tax_rate / decimal.Decimal('100.0')))
            tax_amount = unit_price - subtotal
            grand_total = unit_price

            # 20% down payment
            down_payment = (grand_total * decimal.Decimal('0.20')).quantize(decimal.Decimal('0.01'))
            remaining_balance = grand_total - down_payment

            # Plan duration: 6 months EMI
            num_terms = 6
            monthly_emi = (remaining_balance / decimal.Decimal(str(num_terms))).quantize(decimal.Decimal('0.01'))

            # Set payment status
            scenario = "completed" if i <= 12 else ("active" if i <= 24 else "overdue")
            
            p_status = "paid" if scenario == "completed" else "partial"

            sale = Sale(
                invoice_number=inv_no,
                customer_id=customer.id,
                sale_date=sale_dt,
                subtotal=subtotal.quantize(decimal.Decimal('0.01')),
                discount_amount=decimal.Decimal('0.00'),
                tax_amount=tax_amount.quantize(decimal.Decimal('0.01')),
                grand_total=grand_total,
                down_payment=down_payment,
                remaining_balance=remaining_balance,
                payment_status=p_status,
                sale_status='completed',
                created_at=sale_dt,
                created_by=admin_user_id
            )
            db.session.add(sale)
            db.session.flush()
            sales_created += 1

            # Sale Item
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                quantity=qty,
                unit_price=unit_price,
                discount=decimal.Decimal('0.00'),
                tax=tax_rate,
                total_price=grand_total
            )
            db.session.add(sale_item)

            # Update Product Stock
            if product.current_stock > 0:
                product.current_stock -= qty
                m_out = InventoryMovement(
                    product_id=product.id,
                    movement_type='Stock Out',
                    quantity=qty,
                    previous_stock=product.current_stock + qty,
                    new_stock=product.current_stock,
                    remarks=f"Sold via invoice {inv_no}",
                    created_by=admin_user_id,
                    created_at=sale_dt
                )
                db.session.add(m_out)

            # Customer Debit Ledger entry for full purchase balance
            debit_ledger = CustomerLedger(
                customer_id=customer.id,
                transaction_type='debit',
                reference_id=sale.id,
                description=f"Invoice #{inv_no} purchase credit",
                debit=remaining_balance,
                credit=decimal.Decimal('0.00'),
                balance=remaining_balance,
                transaction_date=sale_dt,
                created_at=sale_dt
            )
            db.session.add(debit_ledger)

            # Create Instalment Plan
            plan_num = f"PLAN-2026-{1000 + i:06d}"
            plan_status = "completed" if scenario == "completed" else ("overdue" if scenario == "overdue" else "active")
            
            plan = InstalmentPlan(
                plan_number=plan_num,
                sale_id=sale.id,
                customer_id=customer.id,
                invoice_number=inv_no,
                total_amount=grand_total,
                down_payment=down_payment,
                remaining_balance=remaining_balance,
                number_of_instalments=num_terms,
                monthly_emi=monthly_emi,
                interest_rate=decimal.Decimal('0.00'),
                processing_fee=decimal.Decimal('0.00'),
                start_date=sale_dt,
                first_due_date=sale_dt + timedelta(days=30),
                last_due_date=sale_dt + timedelta(days=30 * num_terms),
                status=plan_status,
                created_at=sale_dt,
                created_by=admin_user_id
            )
            db.session.add(plan)
            db.session.flush()
            plans_created += 1

            # Down payment record & receipt
            dp_receipt_no = f"RCT-2026-{10000 + (i * 10):06d}"
            dp_payment = Payment(
                receipt_number=dp_receipt_no,
                plan_id=plan.id,
                sale_id=sale.id,
                invoice_number=inv_no,
                customer_id=customer.id,
                payment_amount=down_payment,
                payment_date=sale_dt,
                payment_type='Advance Payment',
                payment_method=random.choice(payment_methods),
                remarks='Down payment collected at sales counter.',
                received_by=admin_user_id,
                payment_status='paid',
                created_at=sale_dt
            )
            db.session.add(dp_payment)
            db.session.flush()
            payments_created += 1

            dp_receipt = PaymentReceipt(
                receipt_number=dp_receipt_no,
                payment_id=dp_payment.id,
                invoice_number=inv_no,
                customer_id=customer.id,
                receipt_date=sale_dt,
                amount_received=down_payment,
                payment_method=dp_payment.payment_method,
                generated_by=admin_user_id
            )
            db.session.add(dp_receipt)

            # Build Instalment Schedules & Monthly Collection Payments
            running_ledger_balance = remaining_balance

            # How many terms are paid?
            if scenario == "completed":
                paid_terms = num_terms
            elif scenario == "active":
                # Spanned terms up to current date
                elapsed_months = max(1, min(num_terms - 1, (today - sale_dt).days // 30))
                paid_terms = elapsed_months
            else: # overdue
                # Missed payment in term 2 or 3
                paid_terms = 1

            for term in range(1, num_terms + 1):
                due_dt = sale_dt + timedelta(days=30 * term)
                
                is_paid = (term <= paid_terms)
                is_overdue = (not is_paid and due_dt < today)

                if is_paid:
                    sched_status = 'paid'
                    paid_amt = monthly_emi
                    bal_amt = decimal.Decimal('0.00')
                    paid_dt = due_dt - timedelta(days=random.randint(0, 3))
                    days_over = 0
                elif is_overdue:
                    sched_status = 'overdue'
                    paid_amt = decimal.Decimal('0.00')
                    bal_amt = monthly_emi
                    paid_dt = None
                    days_over = (today - due_dt).days
                else:
                    sched_status = 'pending'
                    paid_amt = decimal.Decimal('0.00')
                    bal_amt = monthly_emi
                    paid_dt = None
                    days_over = 0

                sched = InstalmentSchedule(
                    plan_id=plan.id,
                    instalment_number=term,
                    due_date=due_dt,
                    amount=monthly_emi,
                    paid_amount=paid_amt,
                    balance=bal_amt,
                    payment_status=sched_status,
                    paid_date=paid_dt,
                    days_overdue=days_over,
                    remarks=f"Instalment term #{term} of {num_terms}"
                )
                db.session.add(sched)
                db.session.flush()

                # If schedule is paid, create payment record & credit ledger entry
                if is_paid:
                    rc_no = f"RCT-2026-{10000 + (i * 10) + term:06d}"
                    pay_method = random.choice(payment_methods)
                    ref_no = f"UPI{random.randint(100000000000, 999999999999)}" if pay_method == 'UPI' else None

                    emi_pay = Payment(
                        receipt_number=rc_no,
                        plan_id=plan.id,
                        schedule_id=sched.id,
                        sale_id=sale.id,
                        invoice_number=inv_no,
                        customer_id=customer.id,
                        payment_amount=monthly_emi,
                        payment_date=paid_dt,
                        payment_type='EMI Payment',
                        payment_method=pay_method,
                        reference_number=ref_no,
                        remarks=f"EMI Payment #{term} received.",
                        received_by=seeded_users[3].id if term % 2 == 0 else admin_user_id,
                        payment_status='paid',
                        created_at=paid_dt
                    )
                    db.session.add(emi_pay)
                    db.session.flush()
                    payments_created += 1

                    emi_receipt = PaymentReceipt(
                        receipt_number=rc_no,
                        payment_id=emi_pay.id,
                        invoice_number=inv_no,
                        customer_id=customer.id,
                        receipt_date=paid_dt,
                        amount_received=monthly_emi,
                        payment_method=pay_method,
                        generated_by=admin_user_id
                    )
                    db.session.add(emi_receipt)

                    # Ledger Credit
                    running_ledger_balance -= monthly_emi
                    credit_ledger = CustomerLedger(
                        customer_id=customer.id,
                        transaction_type='credit',
                        reference_id=emi_pay.id,
                        description=f"EMI Payment #{term} (Receipt: {rc_no})",
                        debit=decimal.Decimal('0.00'),
                        credit=monthly_emi,
                        balance=max(decimal.Decimal('0.00'), running_ledger_balance),
                        transaction_date=paid_dt,
                        created_at=paid_dt
                    )
                    db.session.add(credit_ledger)

        db.session.commit()
        print(f"  - {sales_created} Sales, {plans_created} Plans, and {payments_created} Payments injected.")

        # 9. Reset integer sequences if PostgreSQL
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'postgresql' in db_uri:
            print("  - Resetting PostgreSQL Primary Key sequences...")
            seq_queries = [
                ("roles", "roles_id_seq"),
                ("users", "users_id_seq"),
                ("sale_items", "sale_items_id_seq"),
                ("inventory_movements", "inventory_movements_id_seq"),
                ("audit_logs", "audit_logs_id_seq")
            ]
            for tbl, seq in seq_queries:
                try:
                    db.session.execute(text(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {tbl}), 1));"))
                except Exception as e:
                    db.session.rollback()
            db.session.commit()
            print("  - Sequence numbers reset.")

        print("\nDatabase Fake Data Injection Completed Successfully!")

if __name__ == '__main__':
    seed_fake_data()
