"""Test configuration and fixtures for pytest.

This module contains pytest fixtures that can be used across all tests.
"""

import pytest
from app import create_app
from app.models import db as _db
import os

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'QR_CODE_DIR': os.getenv('QR_CODE_DIR')
    })
    
    # Create tables
    with app.app_context():
        _db.create_all()
        
    yield app
    
    # Clean up
    with app.app_context():
        _db.drop_all()

@pytest.fixture(scope='session')
def client(app):
    """Test client for the application."""
    return app.test_client()

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    return _db

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for each test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    yield db.session
    
    # Rollback transaction
    transaction.rollback()
    connection.close()
    db.session.remove()