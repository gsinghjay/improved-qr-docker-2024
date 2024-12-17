"""Utility module for QR code generation and validation.

This module provides functions for generating QR code images and validating URLs.
It also includes logging setup functionality.
"""

import qrcode
import logging
import validators
from pathlib import Path

def setup_logging():
    """Configure the logging system for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

def create_directory(path: Path):
    """Create a directory if it doesn't exist.
    
    Args:
        path (Path): Path object representing the directory to create
        
    Raises:
        Exception: If directory creation fails
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        raise

def is_valid_url(url):
    """Validate if a given string is a valid URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if validators.url(url):
        return True
    else:
        logging.error(f"Invalid URL provided: {url}")
        return False

def generate_qr_code(data, path, fill_color='red', back_color='white'):
    """Generate a QR code image and save it to the specified path.
    
    Args:
        data (str): The data to encode in the QR code
        path (Path): Path where the QR code image should be saved
        fill_color (str, optional): Color of the QR code pattern. Defaults to 'red'
        back_color (str, optional): Background color. Defaults to 'white'
        
    Returns:
        bool: True if generation successful, False otherwise
    """
    if not is_valid_url(data):
        return False

    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        with path.open('wb') as qr_file:
            img.save(qr_file)
        logging.info(f"QR code successfully saved to {path}")
        return True

    except Exception as e:
        logging.error(f"An error occurred while generating or saving the QR code: {e}")
        return False 