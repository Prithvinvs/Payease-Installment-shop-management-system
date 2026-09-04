"""
Customer forms and validation rules.
"""
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Optional, Length, Regexp, ValidationError

from models.customer import Customer

class CustomerForm(FlaskForm):
    """
    Form validator for customer registration and edit.
    Enforces format standards, uniqueness, and file constraints.
    """
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required."),
        Length(max=50, message="First name cannot exceed 50 characters.")
    ])
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message="Last name is required."),
        Length(max=50, message="Last name cannot exceed 50 characters.")
    ])
    
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[DataRequired(message="Gender selection is required.")])
    
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired(message="Date of birth is required.")
    ])
    
    phone_number = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."),
        Regexp(r'^\+?[0-9]{10,15}$', message="Enter a valid mobile number (10 to 15 digits).")
    ])
    
    alternate_phone = StringField('Alternate Number', validators=[
        Optional(),
        Regexp(r'^\+?[0-9]{10,15}$', message="Enter a valid alternate number (10 to 15 digits).")
    ])
    
    email = StringField('Email Address', validators=[
        Optional(),
        Email(message="Enter a valid email address."),
        Length(max=120)
    ])
    
    # Billing Address
    address_line1 = StringField('Address Line 1', validators=[
        DataRequired(message="Address line 1 is required."),
        Length(max=100)
    ])
    address_line2 = StringField('Address Line 2', validators=[
        Optional(),
        Length(max=100)
    ])
    city = StringField('City', validators=[
        DataRequired(message="City is required."),
        Length(max=50)
    ])
    state = StringField('State', validators=[
        DataRequired(message="State is required."),
        Length(max=50)
    ])
    postal_code = StringField('Postal Code', validators=[
        DataRequired(message="Postal code is required."),
        Length(max=20)
    ])
    country = StringField('Country', default='India', validators=[
        DataRequired(message="Country is required."),
        Length(max=50)
    ])
    
    # Optional demographics
    occupation = StringField('Occupation', validators=[
        Optional(),
        Length(max=50)
    ])
    aadhaar_number = StringField('Aadhaar / ID Number', validators=[
        Optional(),
        Regexp(r'^[0-9]{12}$', message="Aadhaar number must be exactly 12 digits.")
    ])
    profile_photo = FileField('Profile Photo')
    notes = TextAreaField('Additional Notes', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        # Allow passing customer_id to exclude it from unique checks during edits
        self.customer_id = kwargs.pop('customer_id', None)
        super(CustomerForm, self).__init__(*args, **kwargs)

    def validate_phone_number(self, field):
        """
        Validates that phone is unique across non-deleted customers.
        """
        query = Customer.query.filter(
            Customer.phone_number == field.data,
            Customer.deleted_at == None
        )
        if self.customer_id:
            query = query.filter(Customer.id != self.customer_id)
        
        customer = query.first()
        if customer:
            raise ValidationError("This phone number is already registered to another customer.")

    def validate_email(self, field):
        """
        Validates that email is unique if provided.
        """
        if field.data:
            query = Customer.query.filter(
                Customer.email == field.data,
                Customer.deleted_at == None
            )
            if self.customer_id:
                query = query.filter(Customer.id != self.customer_id)
            
            customer = query.first()
            if customer:
                raise ValidationError("This email address is already registered to another customer.")

    def validate_profile_photo(self, field):
        """
        Validates image type and restricts upload size to <= 5MB.
        """
        if field.data and hasattr(field.data, 'filename'):
            filename = field.data.filename
            if filename:
                ext = filename.rsplit('.', 1)[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    raise ValidationError("Allowed image formats are: JPG, JPEG, PNG, WEBP.")
                
                # Check file size
                try:
                    field.data.seek(0, os.SEEK_END)
                    size = field.data.tell()
                    field.data.seek(0) # Reset pointer
                    if size > 5 * 1024 * 1024: # 5MB limit
                        raise ValidationError("Profile photo size must be less than 5 MB.")
                except Exception:
                    pass
