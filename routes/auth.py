"""
Authentication routes blueprint.
Defines endpoints for logging in, logging out, password resets, and session management.
"""
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from database import db
from models.user import User
from models.password_reset import PasswordResetToken
from models.audit_log import AuditLog
from utils.password_validators import validate_password_strength

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    """
    Login WTForm for handling email or username inputs.
    """
    email_or_username = StringField('Username or Email Address', validators=[
        DataRequired(message="Please enter your email or username.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter your password.")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ForgotPasswordForm(FlaskForm):
    """
    Form to request a password reset email link.
    """
    email = StringField('Email Address', validators=[
        DataRequired(message="Email address is required."),
        Email(message="Please enter a valid email address.")
    ])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    """
    Form to enter the new password after resetting.
    """
    password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Update Password')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login controller. Handles brute force locking, credentials check,
    status filtering, and redirects.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.email_or_username.data.strip()
        password_input = form.password.data
        
        # Check by email first, then username
        user = User.query.filter(
            (User.email == login_input) | (User.username == login_input)
        ).first()
        
        if user:
            # 1. Check if user is soft deleted
            if user.deleted_at is not None:
                flash("This account has been deleted.", "danger")
                AuditLog.log('login_failed_deleted', username=login_input)
                return render_template('auth/login.html', form=form)
                
            # 2. Check if user is inactive
            if user.status != 'active':
                flash("This account is currently inactive. Please contact the administrator.", "danger")
                AuditLog.log('login_failed_inactive', user_id=user.id, username=login_input)
                return render_template('auth/login.html', form=form)
                
            # 3. Check brute force lockout status
            if user.is_locked:
                remaining = user.lockout_until - datetime.utcnow()
                minutes_left = int(remaining.total_seconds() / 60) + 1
                flash(f"Account locked due to too many failed attempts. Try again in {minutes_left} minutes.", "danger")
                AuditLog.log('login_failed_locked', user_id=user.id, username=login_input)
                return render_template('auth/login.html', form=form)
                
            # 4. Verify password
            if user.check_password(password_input):
                # Success - reset attempts
                user.login_attempts = 0
                user.lockout_until = None
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Perform login
                login_user(user, remember=form.remember.data)
                
                # Log success
                AuditLog.log('login_success', user_id=user.id, username=user.username)
                
                flash(f"Welcome back, {user.full_name}!", "success")
                
                # Redirect according to role (Staff/Admin/Super Admin all go to dashboard for now,
                # but dynamic sidebar protects access behind standard decorators)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard.index'))
            else:
                # Password mismatch - increment failure counter
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.lockout_until = datetime.utcnow() + timedelta(minutes=15)
                    flash("Too many failed attempts. Your account has been locked for 15 minutes.", "danger")
                    AuditLog.log('lockout_triggered', user_id=user.id, username=user.username)
                else:
                    attempts_left = 5 - user.login_attempts
                    flash(f"Invalid password. You have {attempts_left} attempts remaining.", "warning")
                    AuditLog.log('login_failed_password', user_id=user.id, username=user.username)
                db.session.commit()
        else:
            # User doesn't exist
            flash("User account not found.", "danger")
            AuditLog.log('login_failed_username_not_found', username=login_input)
            
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Signs out user and destroys session.
    """
    user_id = current_user.id
    username = current_user.username
    logout_user()
    
    AuditLog.log('logout', user_id=user_id, username=username)
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password controller. Generates token pair, logs event, and displays simulated URL.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email_input = form.email.data.strip()
        user = User.query.filter_by(email=email_input, deleted_at=None).first()
        
        # If user exists, create token. If not, act as if sent to prevent email harvesting.
        if user:
            # Generate temporary reset token
            raw_token, token_record = PasswordResetToken.generate_token_pair(user_id=user.id)
            db.session.add(token_record)
            db.session.commit()
            
            # Construct reset URL
            reset_url = url_for('auth.reset_password', token=raw_token, _external=True)
            
            # Log action
            AuditLog.log('password_reset_request', user_id=user.id, username=user.username)
            
            # Print to log output (simulating SMTP email server)
            print("\n==================================================")
            print(f"PASSWORD RESET EMAIL SIMULATION (User: {user.username})")
            print(f"To: {user.email}")
            print(f"Reset Link: {reset_url}")
            print("==================================================\n")
            
            # For testing convenience, we flash the link directly in developer environment
            flash(f"[DEV MODE SIMULATION] Reset link sent to {user.email}: {reset_url}", "warning")
        else:
            # Silent logging
            AuditLog.log('password_reset_request_nonexistent_email', username=email_input)
            
        # Standard user-facing message
        flash("If that email is registered in our system, we have sent a secure password reset link.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset password verify controller. Inspects reset token hash and expires constraints.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    # Verify token
    token_record = PasswordResetToken.verify_token(token)
    if not token_record:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for('auth.forgot_password'))
        
    user = token_record.user
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        new_password = form.password.data
        
        # Validate strength
        is_strong, error_msg = validate_password_strength(new_password)
        if not is_strong:
            form.password.errors.append(error_msg)
            return render_template('auth/reset_password.html', form=form, token=token)
            
        # Update password
        user.set_password(new_password)
        # Unlock account in case they were locked out
        user.login_attempts = 0
        user.lockout_until = None
        
        # Mark token as used
        token_record.mark_as_used()
        
        # Save updates
        db.session.commit()
        
        # Audit Log
        AuditLog.log('password_reset_success', user_id=user.id, username=user.username)
        
        flash("Your password has been updated successfully. Please sign in with your new credentials.", "success")
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', form=form, token=token)
