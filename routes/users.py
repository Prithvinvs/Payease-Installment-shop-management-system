"""
Users blueprint.
Defines endpoints for administrative User CRUD operations, status management,
profile edits, profile photo uploads, and security password modifications.
"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

from database import db
from models.user import User
from models.role import Role
from models.audit_log import AuditLog
from utils.auth_decorators import role_required
from utils.password_validators import validate_password_strength

users_bp = Blueprint('users', __name__, url_prefix='/users')

# --- WTForms for User Operations ---

class AddUserForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(message="Full name is required."), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(message="Username is required."), Length(min=3, max=50)])
    email = StringField('Email Address', validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")])
    phone = StringField('Phone Number', validators=[DataRequired(message="Phone number is required."), Length(max=20)])
    role_id = SelectField('System Role', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
    profile_image = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Create User')


class EditUserForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(message="Full name is required."), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(message="Username is required."), Length(min=3, max=50)])
    email = StringField('Email Address', validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")])
    phone = StringField('Phone Number', validators=[DataRequired(message="Phone number is required."), Length(max=20)])
    role_id = SelectField('System Role', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('active', 'Active'), ('inactive', 'Inactive')])
    profile_image = FileField('Change Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Save Changes')


class UpdateProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(message="Full name is required."), Length(max=100)])
    email = StringField('Email Address', validators=[DataRequired(message="Email is required."), Email(message="Invalid email address.")])
    phone = StringField('Phone Number', validators=[DataRequired(message="Phone number is required."), Length(max=20)])
    profile_image = FileField('Change Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    submit = SubmitField('Update Profile')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(message="Current password is required.")])
    new_password = PasswordField('New Password', validators=[DataRequired(message="New password is required.")])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password.")
    ])
    submit = SubmitField('Change Password')


# --- Helper Function for Uploading Images ---

def save_profile_picture(form_picture, user_id):
    """
    Saves a profile picture upload to static/uploads/profile_pics/
    Renames it with a unique hex code to prevent caching and naming clashes.
    """
    _, f_ext = os.path.splitext(form_picture.filename)
    unique_fn = f"{user_id}_{uuid.uuid4().hex}{f_ext}"
    
    # Store uploads inside static directory so they are served correctly by Flask dev server
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_pics')
    
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
        
    full_path = os.path.join(upload_path, unique_fn)
    form_picture.save(full_path)
    
    # Return path relative to static folder
    return f"uploads/profile_pics/{unique_fn}"


# --- Routes ---

@users_bp.route('/')
@login_required
@role_required(['Super Admin'])
def index():
    """
    Displays a list of all active users. Contains search and filters.
    """
    query = User.query.filter_by(deleted_at=None)
    
    # Handle Search
    search_input = request.args.get('search', '').strip()
    if search_input:
        query = query.filter(
            (User.full_name.ilike(f"%{search_input}%")) |
            (User.username.ilike(f"%{search_input}%")) |
            (User.email.ilike(f"%{search_input}%")) |
            (User.phone.ilike(f"%{search_input}%"))
        )
        
    # Handle Status Filter
    status_filter = request.args.get('status', '').strip()
    if status_filter in ['active', 'inactive']:
        query = query.filter_by(status=status_filter)
        
    users_list = query.all()
    return render_template('users/list.html', users=users_list, search=search_input, status=status_filter)


@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required(['Super Admin'])
def add():
    """
    Endpoint to add a new system user.
    """
    form = AddUserForm()
    # Populate role choices dynamically
    form.role_id.choices = [(r.id, r.role_name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()
        phone = form.phone.data.strip()
        password = form.password.data
        
        # Check uniqueness constraints
        errors = False
        if User.query.filter_by(username=username, deleted_at=None).first():
            form.username.errors.append("This username is already taken.")
            errors = True
        if User.query.filter_by(email=email, deleted_at=None).first():
            form.email.errors.append("This email is already registered.")
            errors = True
        if User.query.filter_by(phone=phone, deleted_at=None).first():
            form.phone.errors.append("This phone number is already registered.")
            errors = True
            
        # Validate password strength
        is_strong, strength_err = validate_password_strength(password)
        if not is_strong:
            form.password.errors.append(strength_err)
            errors = True
            
        if errors:
            return render_template('users/add.html', form=form)
            
        # Create User
        new_user = User(
            full_name=form.full_name.data.strip(),
            username=username,
            email=email,
            phone=phone,
            role_id=form.role_id.data,
            status=form.status.data
        )
        new_user.set_password(password)
        
        # Save user to DB to get ID for image path
        db.session.add(new_user)
        db.session.commit()
        
        # Save image if uploaded
        if form.profile_image.data:
            image_path = save_profile_picture(form.profile_image.data, new_user.id)
            new_user.profile_image = image_path
            db.session.commit()
            
        AuditLog.log('user_create', user_id=current_user.id, username=new_user.username)
        flash(f"User {new_user.full_name} created successfully.", "success")
        return redirect(url_for('users.index'))
        
    return render_template('users/add.html', form=form)


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required(['Super Admin'])
def edit(user_id):
    """
    Endpoint to edit user details and roles.
    """
    user = User.query.filter_by(id=user_id, deleted_at=None).first_or_404()
    
    # Prevent editing currently logged in super admin to prevent lockout
    if user.id == current_user.id:
        flash("You cannot edit your own details here. Please use the profile settings page.", "warning")
        return redirect(url_for('users.profile'))
        
    form = EditUserForm(obj=user)
    form.role_id.choices = [(r.id, r.role_name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()
        phone = form.phone.data.strip()
        
        # Check uniqueness constraints excluding this user
        errors = False
        duplicate_username = User.query.filter(User.username == username, User.id != user.id, User.deleted_at == None).first()
        if duplicate_username:
            form.username.errors.append("This username is already taken.")
            errors = True
        duplicate_email = User.query.filter(User.email == email, User.id != user.id, User.deleted_at == None).first()
        if duplicate_email:
            form.email.errors.append("This email is already registered.")
            errors = True
        duplicate_phone = User.query.filter(User.phone == phone, User.id != user.id, User.deleted_at == None).first()
        if duplicate_phone:
            form.phone.errors.append("This phone number is already registered.")
            errors = True
            
        if errors:
            return render_template('users/edit.html', form=form, user=user)
            
        # Update User
        user.full_name = form.full_name.data.strip()
        user.username = username
        user.email = email
        user.phone = phone
        user.role_id = form.role_id.data
        user.status = form.status.data
        
        # Handle file upload
        if form.profile_image.data:
            image_path = save_profile_picture(form.profile_image.data, user.id)
            user.profile_image = image_path
            
        db.session.commit()
        
        AuditLog.log('user_update', user_id=current_user.id, username=user.username)
        flash(f"User {user.full_name} updated successfully.", "success")
        return redirect(url_for('users.index'))
        
    return render_template('users/edit.html', form=form, user=user)


@users_bp.route('/status/<int:user_id>', methods=['POST'])
@login_required
@role_required(['Super Admin'])
def toggle_status(user_id):
    """
    Deactivates or activates a user.
    """
    user = User.query.filter_by(id=user_id, deleted_at=None).first_or_404()
    
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "danger")
        return redirect(url_for('users.index'))
        
    new_status = 'inactive' if user.status == 'active' else 'active'
    user.status = new_status
    db.session.commit()
    
    action = 'user_deactivate' if new_status == 'inactive' else 'user_activate'
    AuditLog.log(action, user_id=current_user.id, username=user.username)
    
    flash(f"User {user.full_name} status updated to {new_status.capitalize()}.", "success")
    return redirect(url_for('users.index'))


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required(['Super Admin'])
def delete(user_id):
    """
    Soft deletes a user.
    """
    user = User.query.filter_by(id=user_id, deleted_at=None).first_or_404()
    
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('users.index'))
        
    # Soft delete user by setting deletion timestamp
    user.deleted_at = datetime.utcnow()
    user.status = 'inactive'
    db.session.commit()
    
    AuditLog.log('user_delete', user_id=current_user.id, username=user.username)
    
    flash(f"User {user.full_name} has been soft-deleted successfully.", "success")
    return redirect(url_for('users.index'))


# --- Profile Route (Accessible by All Logged-in Users) ---

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Displays personal profile page. Handles updates to personal details
    and profile picture upload.
    """
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    
    # Identify which form was submitted
    form_type = request.form.get('form_type')
    
    if form_type == 'profile' and profile_form.validate_on_submit():
        email = profile_form.email.data.strip().lower()
        phone = profile_form.phone.data.strip()
        
        # Check uniqueness excluding self
        errors = False
        duplicate_email = User.query.filter(User.email == email, User.id != current_user.id, User.deleted_at == None).first()
        if duplicate_email:
            profile_form.email.errors.append("This email is already registered.")
            errors = True
        duplicate_phone = User.query.filter(User.phone == phone, User.id != current_user.id, User.deleted_at == None).first()
        if duplicate_phone:
            profile_form.phone.errors.append("This phone number is already registered.")
            errors = True
            
        if not errors:
            current_user.full_name = profile_form.full_name.data.strip()
            current_user.email = email
            current_user.phone = phone
            
            # Handle image upload
            if profile_form.profile_image.data:
                image_path = save_profile_picture(profile_form.profile_image.data, current_user.id)
                current_user.profile_image = image_path
                
            db.session.commit()
            AuditLog.log('profile_update', user_id=current_user.id, username=current_user.username)
            flash("Your profile details have been updated.", "success")
            return redirect(url_for('users.profile'))
            
    elif form_type == 'password' and password_form.validate_on_submit():
        current_password = password_form.current_password.data
        new_password = password_form.new_password.data
        confirm_password = password_form.confirm_password.data
        
        # Verify current password
        errors = False
        if not current_user.check_password(current_password):
            password_form.current_password.errors.append("Incorrect current password.")
            errors = True
            
        # Verify new strength
        is_strong, strength_err = validate_password_strength(new_password)
        if not is_strong:
            password_form.new_password.errors.append(strength_err)
            errors = True
            
        if new_password != confirm_password:
            password_form.confirm_password.errors.append("Confirm password does not match new password.")
            errors = True
            
        if not errors:
            current_user.set_password(new_password)
            db.session.commit()
            AuditLog.log('password_change', user_id=current_user.id, username=current_user.username)
            flash("Your password has been changed successfully.", "success")
            return redirect(url_for('users.profile'))
            
    return render_template('users/profile.html', profile_form=profile_form, password_form=password_form)
