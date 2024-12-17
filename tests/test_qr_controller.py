def test_index_page(client):
    """Test the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200

def test_generate_qr_code(client, session):
    """Test QR code generation."""
    response = client.post('/generate', data={
        'url': 'https://example.com',
        'is_dynamic': 'on',
        'fill_color': 'red',
        'back_color': 'white',
        'description': 'Test QR'
    })
    assert response.status_code == 302  # Redirect after success

    # Verify QR code was created in database
    from app.models.qr_code import QRCode
    qr = session.query(QRCode).first()
    assert qr is not None
    assert qr.url == 'https://example.com'
    assert qr.is_dynamic == True 