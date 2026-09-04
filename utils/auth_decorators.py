"""
Authentication and authorization decorators.
Handles role-based access controls for route protection.
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(allowed_roles):
    """
    Decorator to restrict access to routes based on user role names.
    Usage:
        @app.route('/users')
        @login_required
        @role_required(['Super Admin'])
        def users_list():
            ...
            
    Allowed roles could be 'Super Admin', 'Admin', 'Staff'.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if not current_user.is_authenticated:
                flash("Please log in to access this page.", "warning")
                return redirect(url_for('auth.login'))
            
            # Verify if user's role is in the allowed list
            user_role = current_user.role.role_name if current_user.role else None
            if user_role not in allowed_roles:
                # Aborts request with 403 Forbidden. This triggers our 403 error handler.
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
