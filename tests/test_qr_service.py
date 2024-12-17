import pytest
from app.services.qr_service import QRCodeService
from app.models.qr_code import QRCode
from pathlib import Path

def test_create_qr_code(app, session):
    """Test QR code creation."""
    with app.app_context():
        qr_code, path = QRCodeService.create_qr_code(
            url="https://example.com",
            is_dynamic=True,
            fill_color="blue",
            back_color="white",
            description="Test QR",
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        assert isinstance(qr_code, QRCode)
        assert qr_code.url == "https://example.com"
        assert qr_code.is_dynamic == True
        assert qr_code.short_code is not None
        assert isinstance(path, Path)

def test_update_qr_code(app, session):
    """Test QR code updating."""
    with app.app_context():
        # Create initial QR code
        qr_code, _ = QRCodeService.create_qr_code(
            url="https://example.com",
            is_dynamic=False,
            fill_color="red",
            back_color="white",
            description="Original",
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        # Update QR code
        updated_qr = QRCodeService.update_qr_code(
            qr_code=qr_code,
            url="https://updated.com",
            fill_color="blue",
            back_color="yellow",
            description="Updated",
            is_active=True,
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        assert updated_qr.url == "https://updated.com"
        assert updated_qr.fill_color == "blue"
        assert updated_qr.description == "Updated"

def test_delete_qr_code(app, session):
    """Test QR code deletion."""
    with app.app_context():
        qr_code, path = QRCodeService.create_qr_code(
            url="https://example.com",
            is_dynamic=False,
            fill_color="red",
            back_color="white",
            description="To Delete",
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        QRCodeService.delete_qr_code(qr_code, app.config['QR_CODE_DIR'])
        assert not path.exists()
        assert session.query(QRCode).filter_by(id=qr_code.id).first() is None

def test_increment_access_count(app, session):
    """Test access count incrementing."""
    with app.app_context():
        qr_code, _ = QRCodeService.create_qr_code(
            url="https://example.com",
            is_dynamic=False,
            fill_color="red",
            back_color="white",
            description="Test",
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        initial_count = qr_code.access_count
        QRCodeService.increment_access_count(qr_code)
        assert qr_code.access_count == initial_count + 1

def test_update_qr_code_dynamic(app, session):
    """Test updating dynamic QR code."""
    with app.app_context():
        # Create initial dynamic QR code
        qr_code, _ = QRCodeService.create_qr_code(
            url="https://example.com",
            is_dynamic=True,
            fill_color="red",
            back_color="white",
            description="Original",
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        # Update QR code
        updated_qr = QRCodeService.update_qr_code(
            qr_code=qr_code,
            url="https://updated.com",
            fill_color="blue",
            back_color="yellow",
            description="Updated",
            is_active=True,
            qr_code_dir=app.config['QR_CODE_DIR']
        )
        
        assert updated_qr.url == "https://updated.com"
        assert updated_qr.is_dynamic == True
        assert updated_qr.short_code is not None

def test_validate_url(app):
    """Test URL validation."""
    with app.app_context():
        assert QRCodeService.validate_url("https://example.com") == True
        assert QRCodeService.validate_url("not_a_url") == False

def test_generate_qr_image(app, tmp_path):
    """Test QR image generation."""
    with app.app_context():
        path = tmp_path / "test.png"
        result = QRCodeService.generate_qr_image(
            url="https://example.com",
            path=path,
            fill_color="red",
            back_color="white"
        )
        assert result == True
        assert path.exists()