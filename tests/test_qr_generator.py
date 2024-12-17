import pytest
from pathlib import Path
from app.utils.qr_generator import setup_logging, create_directory, is_valid_url, generate_qr_code

def test_setup_logging():
    """Test logging setup."""
    setup_logging()
    # Success if no exception raised

def test_create_directory(tmp_path):
    """Test directory creation."""
    test_dir = tmp_path / "test_qr_codes"
    create_directory(test_dir)
    assert test_dir.exists()
    
    # Test creating existing directory
    create_directory(test_dir)  # Should not raise exception
    
def test_create_directory_error(monkeypatch):
    """Test directory creation error handling."""
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")
    
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)
    with pytest.raises(Exception):
        create_directory(Path("/invalid/path"))

def test_is_valid_url():
    """Test URL validation."""
    # Test valid URLs
    assert is_valid_url("https://example.com") == True
    assert is_valid_url("https://sub.example.com/path?param=1") == True
    
    # Test invalid URLs
    assert is_valid_url("not_a_url") == False
    assert is_valid_url("") == False
    
    # Note: localhost URLs are considered invalid in production for security
    assert is_valid_url("http://localhost:5000") == False

def test_generate_qr_code(tmp_path):
    """Test QR code generation."""
    test_path = tmp_path / "test.png"
    
    # Test successful generation
    assert generate_qr_code("https://example.com", test_path) == True
    assert test_path.exists()
    
    # Test invalid URL
    assert generate_qr_code("invalid_url", test_path) == False

def test_generate_qr_code_error(tmp_path, monkeypatch):
    """Test QR code generation error handling."""
    def mock_save(*args, **kwargs):
        raise IOError("Save failed")
    
    # Correctly mock the QRCode make_image method
    class MockImage:
        def save(self, *args, **kwargs):
            raise IOError("Save failed")
            
    class MockQR:
        def make_image(self, *args, **kwargs):
            return MockImage()
        
        def add_data(self, *args, **kwargs):
            pass
            
        def make(self, *args, **kwargs):
            pass
    
    monkeypatch.setattr("qrcode.QRCode", lambda *args, **kwargs: MockQR())
    
    test_path = tmp_path / "error.png"
    assert generate_qr_code("https://example.com", test_path) == False