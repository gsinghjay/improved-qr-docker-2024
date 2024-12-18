"""Test configuration and fixtures for pytest.

This module contains pytest fixtures that can be used across all tests.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.models import db as _db

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a temporary directory for QR codes during testing
    test_qr_dir = Path('test_qr_codes')
    test_qr_dir.mkdir(exist_ok=True)
    
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['GROQ_API_KEY'] = 'test_key'
    os.environ['GROQ_MODEL'] = 'mixtral-8x7b-32768'
    
    # Create the app
    app = create_app()
    
    # Override the database configuration for testing
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'QR_CODE_DIR': str(test_qr_dir),
        'SECRET_KEY': 'test_key',
        'WTF_CSRF_ENABLED': False
    })
    
    # Initialize the database
    with app.app_context():
        _db.create_all()
    
    yield app
    
    # Clean up
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
    
    # Remove test QR code directory
    if test_qr_dir.exists():
        import shutil
        shutil.rmtree(test_qr_dir)

@pytest.fixture(scope='function')
def client(app):
    """Test client for the application."""
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    """Database fixture for tests."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def session(app):
    """Creates a new database session for each test."""
    with app.app_context():
        _db.session.begin_nested()
        yield _db.session
        _db.session.rollback()