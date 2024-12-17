from flask import Flask
import os
from .models import init_db
from .controllers.qr_controller import qr_bp

def create_app():
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