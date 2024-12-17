"""Flask application factory module.

This module contains the application factory function that creates
and configures the Flask application instance.
"""

from flask import Flask
import os
from .models import init_db
from .controllers.qr_controller import qr_bp

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['QR_CODE_DIR'] = os.getenv('QR_CODE_DIR', 'qr_codes')

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(qr_bp)

    return app 