"""Database initialization module.

This module provides functionality to initialize and configure the SQLAlchemy
database instance used by the application.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask application.
    
    Args:
        app (Flask): The Flask application instance
    """
    db.init_app(app)
    with app.app_context():
        db.create_all() 