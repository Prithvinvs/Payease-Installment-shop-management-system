"""
Customer REST API blueprint.
Provides JSON APIs for frontend integrations, search fields, and mobile layouts.
"""
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from database import db
from models.customer import Customer
from models.audit_log import AuditLog

customers_api_bp = Blueprint('customers_api', __name__, url_prefix='/api/customers')

# Helper function to convert Customer model to dict representation
def customer_to_dict(c):
    return {
        'id': c.id,
        'customer_code': c.customer_code,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'full_name': c.full_name,
        'phone_number': c.phone_number,
        'alternate_phone': c.alternate_phone or '',
        'email': c.email or '',
        'address_line1': c.address_line1,
        'address_line2': c.address_line2 or '',
        'city': c.city,
        'state': c.state,
        'postal_code': c.postal_code,
        'country': c.country,
        'date_of_birth': c.date_of_birth.strftime('%Y-%m-%d'),
        'gender': c.gender,
        'occupation': c.occupation or '',
        'aadhaar_number': c.aadhaar_number or '',
        'profile_photo': c.profile_photo or '',
        'status': c.status,
        'outstanding_balance': c.outstanding_balance,
        'total_purchases': c.total_purchases,
        'total_payments': c.total_payments,
        'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
    }

@customers_api_bp.route('', methods=['GET'])
@login_required
def get_all():
    """
    GET /api/customers
    Returns list of all active non-deleted customers.
    """
    customers = Customer.query.filter_by(deleted_at=None).all()
    return jsonify([customer_to_dict(c) for c in customers]), 200

@customers_api_bp.route('/<string:id>', methods=['GET'])
@login_required
def get_one(id):
    """
    GET /api/customers/<id>
    Returns customer details by primary ID.
    """
    customer = Customer.query.filter_by(id=id, deleted_at=None).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    return jsonify(customer_to_dict(customer)), 200

@customers_api_bp.route('', methods=['POST'])
@login_required
def create_customer():
    """
    POST /api/customers
    Accepts JSON body and creates a customer record.
    """
    data = request.get_json() or {}
    
    # Required validation
    required_fields = ['first_name', 'last_name', 'phone_number', 'address_line1', 'city', 'state', 'postal_code', 'date_of_birth', 'gender']
    missing = [f for f in required_fields if f not in data or not str(data[f]).strip()]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400
        
    # Check phone duplicate
    phone = str(data['phone_number']).strip()
    if Customer.query.filter_by(phone_number=phone, deleted_at=None).first():
        return jsonify({'error': 'Phone number already registered'}), 409
        
    # Calculate next customer code
    last_customer = Customer.query.order_by(Customer.customer_code.desc()).first()
    if last_customer:
        try:
            num = int(last_customer.customer_code.replace("CUST", ""))
            code = f"CUST{num + 1:04d}"
        except ValueError:
            code = "CUST0001"
    else:
        code = "CUST0001"
        
    try:
        dob_val = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date_of_birth format. Use YYYY-MM-DD.'}), 400

    customer = Customer(
        customer_code=code,
        first_name=data['first_name'],
        last_name=data['last_name'],
        full_name=f"{data['first_name']} {data['last_name']}",
        phone_number=phone,
        alternate_phone=data.get('alternate_phone'),
        email=data.get('email'),
        address_line1=data['address_line1'],
        address_line2=data.get('address_line2'),
        city=data['city'],
        state=data['state'],
        postal_code=data['postal_code'],
        country=data.get('country', 'India'),
        date_of_birth=dob_val,
        gender=data['gender'],
        occupation=data.get('occupation'),
        aadhaar_number=data.get('aadhaar_number'),
        notes=data.get('notes'),
        created_by=current_user.id,
        status='active'
    )
    
    db.session.add(customer)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"api_customer_create: {code}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(customer_to_dict(customer)), 201

@customers_api_bp.route('/<string:id>', methods=['PUT'])
@login_required
def update_customer(id):
    """
    PUT /api/customers/<id>
    Accepts JSON body and updates a customer record.
    """
    customer = Customer.query.filter_by(id=id, deleted_at=None).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    data = request.get_json() or {}
    
    # Check phone uniqueness
    if 'phone_number' in data and data['phone_number'].strip() != customer.phone_number:
        phone = data['phone_number'].strip()
        existing = Customer.query.filter(Customer.phone_number == phone, Customer.id != id, Customer.deleted_at == None).first()
        if existing:
            return jsonify({'error': 'Phone number already registered to another customer'}), 409
        customer.phone_number = phone
        
    # Check email uniqueness
    if 'email' in data and data['email'] and data['email'].strip() != customer.email:
        email = data['email'].strip()
        existing = Customer.query.filter(Customer.email == email, Customer.id != id, Customer.deleted_at == None).first()
        if existing:
            return jsonify({'error': 'Email already registered to another customer'}), 409
        customer.email = email

    # Optional bindings
    for field in ['first_name', 'last_name', 'alternate_phone', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'gender', 'occupation', 'aadhaar_number', 'notes', 'status']:
        if field in data:
            setattr(customer, field, data[field])
            
    # Regenerate full name if first or last name changes
    customer.full_name = f"{customer.first_name} {customer.last_name}"
            
    if 'date_of_birth' in data:
        try:
            customer.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date_of_birth format. Use YYYY-MM-DD.'}), 400
            
    customer.updated_by = current_user.id
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"api_customer_update: {customer.customer_code}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify(customer_to_dict(customer)), 200

@customers_api_bp.route('/<string:id>', methods=['DELETE'])
@login_required
def delete_customer(id):
    """
    DELETE /api/customers/<id>
    Restricted to Super Admin or Admin. Soft deletes a customer.
    """
    if current_user.role.role_name not in ['Super Admin', 'Admin']:
        return jsonify({'error': 'Unauthorized permission. Admins only.'}), 403
        
    customer = Customer.query.filter_by(id=id, deleted_at=None).first()
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
        
    if customer.outstanding_balance > 0:
        return jsonify({'error': 'Cannot delete customer with an active outstanding balance'}), 400
        
    customer.deleted_at = datetime.utcnow()
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action=f"api_customer_delete: {customer.customer_code}",
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'message': 'Customer soft-deleted successfully'}), 200

@customers_api_bp.route('/search', methods=['GET'])
@login_required
def search_customers():
    """
    GET /api/customers/search?q=value
    Queries customer records matching name, phone, code, email, city.
    """
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([]), 200
        
    results = Customer.query.filter(
        Customer.deleted_at == None
    ).filter(
        (Customer.full_name.ilike(f"%{q}%")) |
        (Customer.phone_number.ilike(f"%{q}%")) |
        (Customer.customer_code.ilike(f"%{q}%")) |
        (Customer.email.ilike(f"%{q}%")) |
        (Customer.city.ilike(f"%{q}%"))
    ).limit(20).all()
    
    return jsonify([customer_to_dict(c) for c in results]), 200
