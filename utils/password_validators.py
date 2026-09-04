"""
Utility functions for password validation and security enforcement.
"""
import re

def validate_password_strength(password):
    """
    Validates that a password satisfies complexity requirements:
    - Minimum 8 characters, maximum 64 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one numerical digit (0-9)
    - At least one special character (e.g. !@#$%^&* etc.)
    
    Returns: (is_strong, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 64:
        return False, "Password cannot exceed 64 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};':\",\./<>\?\|\\`~]", password):
        return False, "Password must contain at least one special character (e.g., !@#$%^&*)."
        
    return True, ""
