"""
Role model representing user permissions and access rights.
"""
from database import db

class Role(db.Model):
    """
    Role table mapping.
    1 = Super Admin (all access)
    2 = Admin (shop owner)
    3 = Staff (cashier/operator)
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    users = db.relationship('User', back_populates='role', lazy=True)

    def __repr__(self):
        return f"<Role {self.role_name}>"
