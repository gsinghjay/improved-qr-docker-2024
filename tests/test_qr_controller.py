import pytest
from app.models.qr_code import QRCode
from unittest.mock import patch

def test_index_page(client):
    """Test the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200

def test_generate_qr_invalid_url(client):
    """Test QR code generation with invalid URL."""
    response = client.post('/generate', data={
        'url': 'invalid_url',
        'is_dynamic': 'on'
    }, follow_redirects=True)
    
    assert b'Invalid URL provided' in response.data

def test_redirect_qr(client, session):
    """Test QR code redirection."""
    # Create a QR code first
    qr_code = QRCode(url='https://example.com', filename='test.png', short_code='test123')
    session.add(qr_code)
    session.commit()
    
    response = client.get(f'/r/{qr_code.short_code}')
    assert response.status_code == 302
    assert response.location == 'https://example.com'

def test_edit_qr(client, session):
    """Test QR code editing."""
    # Create a QR code first
    qr_code = QRCode(url='https://example.com', filename='test.png')
    session.add(qr_code)
    session.commit()
    
    # Test GET request
    response = client.get(f'/qr/{qr_code.id}/edit')
    assert response.status_code == 200
    
    # Test POST request
    response = client.post(f'/qr/{qr_code.id}/edit', data={
        'url': 'https://updated.com',
        'fill_color': 'blue',
        'back_color': 'yellow',
        'description': 'Updated QR',
        'is_active': 'on'
    })
    assert response.status_code == 302

def test_delete_qr(client, session):
    """Test QR code deletion."""
    qr_code = QRCode(url='https://example.com', filename='test.png')
    session.add(qr_code)
    session.commit()
    
    response = client.post(f'/qr/{qr_code.id}/delete')
    assert response.status_code == 302
    assert session.query(QRCode).filter_by(id=qr_code.id).first() is None

def test_dynamic_redirect(client, session):
    """Test dynamic QR code redirection."""
    # Create a QR code first
    qr_code = QRCode(
        url='https://example.com',
        filename='test.png',
        is_dynamic=True,
        short_code='dyn123',
        is_active=True
    )
    
    # Set redirect_url after creation
    session.add(qr_code)
    session.flush()  # Ensure the object is created in the session
    qr_code.redirect_url = 'https://redirect.com'
    session.commit()
    
    # Test with redirect_url
    response = client.get(f'/d/{qr_code.short_code}')
    assert response.status_code == 302
    assert response.location == 'https://redirect.com'
    
    # Test fallback to original url when redirect_url is None
    qr_code.redirect_url = None
    session.commit()
    response = client.get(f'/d/{qr_code.short_code}')
    assert response.status_code == 302
    assert response.location == 'https://example.com'

def test_view_qr_details(client, session):
    """Test QR code details view."""
    qr_code = QRCode(url='https://example.com', filename='test.png')
    session.add(qr_code)
    session.commit()
    
    response = client.get(f'/qr/{qr_code.id}/view')
    assert response.status_code == 200

def test_generate_qr_code(client, session, tmp_path):
    """Test QR code generation with valid data."""
    with client.application.app_context():
        # Set temporary QR code directory
        client.application.config['QR_CODE_DIR'] = str(tmp_path)
        
        response = client.post('/generate', data={
            'url': 'https://example.com',
            'is_dynamic': 'on',  # Flask form data sends 'on' for checked checkboxes
            'fill_color': 'blue',
            'back_color': 'white',
            'description': 'Test QR'
        }, follow_redirects=True)
        
        assert b'QR Code generated successfully!' in response.data
        qr_code = QRCode.query.order_by(QRCode.id.desc()).first()  # Get the most recent QR code
        assert qr_code is not None
        assert qr_code.url == 'https://example.com'
        assert qr_code.is_dynamic == True
        assert qr_code.short_code is not None
        assert qr_code.fill_color == 'blue'
        assert qr_code.back_color == 'white'
        assert qr_code.description == 'Test QR'

def test_generate_qr_code_static(client, session, tmp_path):
    """Test static QR code generation."""
    with client.application.app_context():
        # Set temporary QR code directory
        client.application.config['QR_CODE_DIR'] = str(tmp_path)
        
        # Clear any existing QR codes
        session.query(QRCode).delete()
        session.commit()
        
        response = client.post('/generate', data={
            'url': 'https://example.com',
            # is_dynamic not included, should default to False
            'fill_color': 'red',
            'back_color': 'white',
            'description': 'Static QR'
        }, follow_redirects=True)
        
        assert b'QR Code generated successfully!' in response.data
        qr_code = QRCode.query.first()
        assert qr_code is not None
        assert qr_code.url == 'https://example.com'
        assert qr_code.is_dynamic == False
        assert qr_code.short_code is None  # Static QR codes should not have a short code
        assert qr_code.fill_color == 'red'
        assert qr_code.back_color == 'white'
        assert qr_code.description == 'Static QR'

def test_serve_qr_code(client, session, tmp_path):
    """Test serving QR code images."""
    # Create a test file
    test_file = tmp_path / "test.png"
    test_file.write_bytes(b"test image data")
    
    with client.application.app_context():
        client.application.config['QR_CODE_DIR'] = str(tmp_path)
        response = client.get('/qr_codes/test.png')
        assert response.status_code == 200
        assert response.data == b"test image data"

def test_short_code_collision(client, session):
    """Test short code generation with collision."""
    with client.application.app_context():
        # Create first QR code with a specific short code
        qr_code1 = QRCode(
            url='https://example1.com',
            filename='test1.png',
            is_dynamic=True,
            short_code='test123'
        )
        session.add(qr_code1)
        session.commit()
        
        # Create second QR code
        qr_code2 = QRCode(
            url='https://example2.com',
            filename='test2.png',
            is_dynamic=True
        )
        session.add(qr_code2)
        session.commit()
        
        # Verify the important conditions
        assert qr_code1.short_code != qr_code2.short_code  # Codes should be unique
        assert len(qr_code2.short_code) == 8  # Length should be 8
        assert QRCode.query.filter_by(short_code=qr_code2.short_code).count() == 1  # Should be unique in DB