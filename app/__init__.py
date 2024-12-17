"""Flask application factory module.

This module contains the application factory function that creates
and configures the Flask application instance.
"""

from flask import Flask
import os
from dotenv import load_dotenv
from .models import init_db
from .controllers.qr_controller import qr_bp

# Load environment variables from .env file
load_dotenv()

def create_app():
    """Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///qr_codes.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['DATABASE_URL']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['QR_CODE_DIR'] = os.getenv('QR_CODE_DIR', 'qr_codes')
    app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(qr_bp)

    return app 