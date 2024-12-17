"""Database migration management script.

This script provides commands for managing database migrations using Flask-Migrate.
It allows creating new migrations, upgrading the database, and rolling back changes.
"""

from flask.cli import FlaskGroup
from flask_migrate import Migrate
from app import create_app, models
from app.models import db

app = create_app()
migrate = Migrate(app, db)
cli = FlaskGroup(app)

if __name__ == '__main__':
    cli() 