"""
Setting model representing global application configuration key-value storage.
"""
from database import db

class Setting(db.Model):
    """
    Settings table mapping.
    Stores shop descriptors, code prefixes, and timezones.
    """
    __tablename__ = 'settings'

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=True)

    @staticmethod
    def get_val(key, default=None):
        """
        Retrieves the value for a given key.
        """
        item = Setting.query.filter_by(key=key).first()
        return item.value if item else default

    @staticmethod
    def set_val(key, value):
        """
        Sets the value for a given key.
        """
        item = Setting.query.filter_by(key=key).first()
        if not item:
            item = Setting(key=key, value=value)
            db.session.add(item)
        else:
            item.value = value
        db.session.commit()

    def __repr__(self):
        return f"<Setting {self.key}: {self.value}>"
