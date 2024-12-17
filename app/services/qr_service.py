"""Service module for handling QR code business logic.

This module provides a service layer that handles the business logic for
QR code operations including creation, updating, deletion, and validation.
"""

from pathlib import Path
from datetime import datetime
from ..models.qr_code import QRCode
from ..models import db
from ..utils.qr_generator import generate_qr_code, is_valid_url

class QRCodeService:
    """Service class for handling QR code operations."""
    
    @staticmethod
    def create_qr_code(url, is_dynamic, fill_color, back_color, description, qr_code_dir):
        """Create a new QR code record and generate the QR code image.
        
        Args:
            url (str): The URL to encode in the QR code
            is_dynamic (bool): Whether this is a dynamic QR code
            fill_color (str): Color for the QR code pattern
            back_color (str): Background color for the QR code
            description (str): Optional description of the QR code
            qr_code_dir (str): Directory to store the QR code image
            
        Returns:
            tuple: (QRCode, Path) The created QR code object and the path to the image
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"QRCode_{timestamp}.png"
        path = Path(qr_code_dir) / filename

        qr_code = QRCode(
            url=url,
            filename=filename,
            fill_color=fill_color,
            back_color=back_color,
            description=description,
            is_dynamic=is_dynamic
        )
        
        db.session.add(qr_code)
        db.session.commit()

        return qr_code, path

    @staticmethod
    def update_qr_code(qr_code, url, fill_color, back_color, description, is_active, qr_code_dir):
        """Update an existing QR code record and regenerate the image if needed.
        
        Args:
            qr_code (QRCode): The QR code object to update
            url (str): New URL for the QR code
            fill_color (str): New fill color for the QR code
            back_color (str): New background color for the QR code
            description (str): New description for the QR code
            is_active (bool): New active status for the QR code
            qr_code_dir (str): Directory containing QR code images
            
        Returns:
            QRCode: The updated QR code object
        """
        qr_code.url = url
        qr_code.fill_color = fill_color
        qr_code.back_color = back_color
        qr_code.description = description
        qr_code.is_active = is_active
        
        db.session.commit()

        if not qr_code.is_dynamic:
            path = Path(qr_code_dir) / qr_code.filename
            generate_qr_code(qr_code.url, path, qr_code.fill_color, qr_code.back_color)

        return qr_code

    @staticmethod
    def delete_qr_code(qr_code, qr_code_dir):
        """Delete a QR code record and its associated image file.
        
        Args:
            qr_code (QRCode): The QR code object to delete
            qr_code_dir (str): Directory containing QR code images
        """
        path = Path(qr_code_dir) / qr_code.filename
        if path.exists():
            path.unlink()
            
        db.session.delete(qr_code)
        db.session.commit()

    @staticmethod
    def increment_access_count(qr_code):
        """Increment the access count for a QR code.
        
        Args:
            qr_code (QRCode): The QR code object to update
        """
        qr_code.access_count += 1
        db.session.commit()

    @staticmethod
    def validate_url(url):
        """Validate if a URL is properly formatted.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL is valid, False otherwise
        """
        return is_valid_url(url)

    @staticmethod
    def generate_qr_image(url, path, fill_color, back_color):
        """Generate a QR code image file.
        
        Args:
            url (str): URL to encode in the QR code
            path (Path): Path where the image should be saved
            fill_color (str): Color for the QR code pattern
            back_color (str): Background color for the QR code
            
        Returns:
            bool: True if generation successful, False otherwise
        """
        return generate_qr_code(url, path, fill_color, back_color) 