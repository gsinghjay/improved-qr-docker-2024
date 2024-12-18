import pytest
from app.services.qr_service import QRCodeService
from app.models.qr_code import QRCode
from pathlib import Path
import shutil

@pytest.fixture
def qr_code_dir(tmp_path):
    """Create temporary directory for QR codes."""
    qr_dir = tmp_path / "qr_codes"
    qr_dir.mkdir()
    yield qr_dir
    shutil.rmtree(qr_dir)

@pytest.mark.usefixtures('session')
class TestQRCodeService:
    def test_create_qr_code(self, app, qr_code_dir):
        """Test QR code creation with all parameters."""
        with app.app_context():
            qr_code, path = QRCodeService.create_qr_code(
                url="https://example.com",
                is_dynamic=True,
                fill_color="blue",
                back_color="white",
                description="Test QR",
                qr_code_dir=qr_code_dir
            )
            
            assert isinstance(qr_code, QRCode)
            assert qr_code.url == "https://example.com"
            assert qr_code.is_dynamic == True
            assert qr_code.fill_color == "blue"
            assert path.exists()

    def test_update_qr_code(self, app, qr_code_dir):
        """Test QR code updating with file operations."""
        with app.app_context():
            # Create initial QR code
            qr_code, path = QRCodeService.create_qr_code(
                url="https://example.com",
                is_dynamic=False,
                qr_code_dir=qr_code_dir
            )
            
            # Update QR code
            updated = QRCodeService.update_qr_code(
                qr_code=qr_code,
                url="https://updated.com",
                fill_color="red",
                back_color="yellow",
                description="Updated QR",
                is_active=True,
                filename=qr_code.filename,
                qr_code_dir=qr_code_dir
            )
            
            assert updated.url == "https://updated.com"
            assert updated.fill_color == "red"
            assert path.exists()

    # ... rest of the test methods with similar app.app_context() usage ...