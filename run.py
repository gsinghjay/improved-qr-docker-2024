"""Application entry point.

This module serves as the entry point for running the Flask application.
It configures logging and starts the development server.
"""

from flask import Flask
from flask_migrate import Migrate
from app import create_app
from app.models import db
from app.utils.qr_generator import setup_logging

def create_migration_app():
    """Create Flask application with migration support."""
    app = create_app()
    Migrate(app, db)
    return app

app = create_migration_app()

if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=5000, debug=True) 