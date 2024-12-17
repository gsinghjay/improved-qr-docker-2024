import pytest
from app.models.qr_code import QRCode

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