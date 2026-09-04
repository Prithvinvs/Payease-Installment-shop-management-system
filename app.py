"""
Main Application Factory for the Instalment Shop Management System.
Responsible for setting up Flask configurations, database bindings, extensions,
registering Blueprints, error handling, and session management.
"""
import os
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime

from config import Config
from database import db, init_db

from flask_wtf.csrf import CSRFProtect

# Initialize Flask extensions
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    """
    Application factory pattern to create and configure the Flask app.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure folder paths exist
    for folder in [app.config['INVOICES_FOLDER'], app.config['REPORTS_FOLDER'], app.config['UPLOADS_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # Initialize extensions with app
    init_db(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    # Register user loader for authentication
    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.dashboard import dashboard_bp
    from routes.auth import auth_bp
    from routes.users import users_bp
    from routes.dashboard_api import dashboard_api_bp
    from routes.customers import customers_bp
    from routes.customers_api import customers_api_bp
    from routes.products import products_bp
    from routes.categories import categories_bp
    from routes.brands import brands_bp
    from routes.inventory import inventory_bp
    from routes.products_api import products_api_bp
    from routes.sales import sales_bp
    from routes.sales_api import sales_api_bp
    from routes.instalments import instalments_bp
    from routes.instalments_api import instalments_api_bp
    from routes.payments import payments_bp
    from routes.payments_api import payments_api_bp
    from routes.reports import reports_bp
    from routes.reports_api import reports_api_bp
    from routes.settings import settings_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp)
    app.register_blueprint(dashboard_api_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(customers_api_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(brands_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(products_api_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(sales_api_bp)
    app.register_blueprint(instalments_bp)
    app.register_blueprint(instalments_api_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(payments_api_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(reports_api_bp)
    app.register_blueprint(settings_bp)

    # Exempt APIs from CSRF protection to support programmatic JSON clients
    csrf.exempt(customers_api_bp)
    csrf.exempt(products_api_bp)
    csrf.exempt(dashboard_api_bp)
    csrf.exempt(sales_api_bp)
    csrf.exempt(instalments_api_bp)
    csrf.exempt(payments_api_bp)
    csrf.exempt(reports_api_bp)

    # Inject current year into all templates (useful for footer copyright)
    @app.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().year}

    # Error handling routes
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
