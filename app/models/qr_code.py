"""QR Code model module for storing QR code information in the database.

This module defines the QRCode model class which represents the database schema
for storing QR codes and their associated metadata.
"""

from datetime import datetime
import secrets
from . import db

class QRCode(db.Model):
    """SQLAlchemy model representing a QR code in the database.
    
    Attributes:
        id (int): Primary key for the QR code record
        url (str): The URL that the QR code points to
        filename (str): Name of the file where the QR code image is stored
        fill_color (str): Color used for the QR code pattern
        back_color (str): Background color of the QR code
        created_at (datetime): Timestamp when the QR code was created
        updated_at (datetime): Timestamp when the QR code was last updated
        is_active (bool): Whether the QR code is currently active
        description (str): Optional description of the QR code
        access_count (int): Number of times the QR code has been scanned
        is_dynamic (bool): Whether this is a dynamic QR code
        short_code (str): Unique identifier for dynamic QR codes
    """

    __tablename__ = 'qr_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    fill_color = db.Column(db.String(50), default='red')
    back_color = db.Column(db.String(50), default='white')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(500))
    access_count = db.Column(db.Integer, default=0)
    is_dynamic = db.Column(db.Boolean, default=False)
    short_code = db.Column(db.String(16), unique=True)

    def __init__(self, **kwargs):
        super(QRCode, self).__init__(**kwargs)
        if self.is_dynamic and not self.short_code:
            self.short_code = self.generate_short_code()

    def generate_short_code(self):
        """Generate a unique short code for dynamic QR codes.
        
        Returns:
            str: A unique 8-character URL-safe token
        """
        while True:
            code = secrets.token_urlsafe(8)[:8]
            if not QRCode.query.filter_by(short_code=code).first():
                return code

    def __repr__(self):
        return f'<QRCode {self.id}: {self.url}>' 