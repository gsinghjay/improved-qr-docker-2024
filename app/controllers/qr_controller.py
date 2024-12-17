"""Controller module for handling QR code-related HTTP requests.

This module defines the routes and request handling logic for the QR code
generation and management system.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from ..models.qr_code import QRCode
from ..services.qr_service import QRCodeService
from flask import current_app

qr_bp = Blueprint('qr', __name__, url_prefix='')

@qr_bp.route('/')
def index():
    """Route handler for the home page.
    
    Returns:
        str: Rendered HTML template with list of QR codes
    """
    qr_codes = QRCode.query.order_by(QRCode.created_at.desc()).all()
    return render_template('index.html', qr_codes=qr_codes)

@qr_bp.route('/generate', methods=['POST'])
def generate():
    """Handle QR code generation requests.
    
    Returns:
        Response: Redirect to index page with success/error message
    """
    url = request.form.get('url')
    is_dynamic = request.form.get('is_dynamic') == 'on'
    
    if not url or not QRCodeService.validate_url(url):
        flash('Invalid URL provided', 'error')
        return redirect(url_for('qr.index'))

    qr_code, path = QRCodeService.create_qr_code(
        url=url,
        is_dynamic=is_dynamic,
        fill_color=request.form.get('fill_color', 'red'),
        back_color=request.form.get('back_color', 'white'),
        description=request.form.get('description', ''),
        qr_code_dir=current_app.config['QR_CODE_DIR']
    )

    # Generate QR code with dynamic or static URL
    qr_url = url_for('qr.redirect_qr', short_code=qr_code.short_code, _external=True) if is_dynamic else url
    QRCodeService.generate_qr_image(qr_url, path, qr_code.fill_color, qr_code.back_color)
    
    flash('QR Code generated successfully!', 'success')
    return redirect(url_for('qr.index'))

@qr_bp.route('/r/<short_code>')
def redirect_qr(short_code):
    """Handle redirection for QR code short codes.
    
    Args:
        short_code (str): The short code to look up
        
    Returns:
        Response: Redirect to the target URL
    """
    qr_code = QRCode.query.filter_by(short_code=short_code, is_active=True).first_or_404()
    QRCodeService.increment_access_count(qr_code)
    return redirect(qr_code.url)

@qr_bp.route('/qr/<int:qr_id>/edit', methods=['GET', 'POST'])
def edit_qr(qr_id):
    """Handle QR code editing requests."""
    qr_code = QRCode.query.get_or_404(qr_id)
    
    if request.method == 'POST':
        # Validate filename if provided
        new_filename = request.form.get('filename')
        if new_filename and not QRCodeService.validate_filename(new_filename):
            flash('Invalid filename. Use only letters, numbers, hyphens and underscores.', 'error')
            return render_template('edit.html', qr_code=qr_code)

        qr_code = QRCodeService.update_qr_code(
            qr_code=qr_code,
            url=request.form['url'],
            fill_color=request.form.get('fill_color', 'red'),
            back_color=request.form.get('back_color', 'white'),
            description=request.form.get('description', ''),
            filename=new_filename,
            is_active='is_active' in request.form,
            qr_code_dir=current_app.config['QR_CODE_DIR']
        )
        
        flash('QR Code updated successfully!', 'success')
        return redirect(url_for('qr.index'))
        
    return render_template('edit.html', qr_code=qr_code)

@qr_bp.route('/qr/<int:qr_id>/delete', methods=['POST'])
def delete_qr(qr_id):
    """Handle QR code deletion requests.
    
    Args:
        qr_id (int): ID of the QR code to delete
        
    Returns:
        Response: Redirect to index page
    """
    qr_code = QRCode.query.get_or_404(qr_id)
    QRCodeService.delete_qr_code(qr_code, current_app.config['QR_CODE_DIR'])
    
    flash('QR Code deleted successfully!', 'success')
    return redirect(url_for('qr.index'))

@qr_bp.route('/qr_codes/<path:filename>')
def serve_qr_code(filename):
    """Serve a QR code image file.
    
    Args:
        filename (str): Name of the QR code image file
        
    Returns:
        Response: The requested image file
    """
    return send_from_directory(current_app.config['QR_CODE_DIR'], filename)

@qr_bp.route('/d/<short_code>')
def dynamic_redirect(short_code):
    """Handle redirection for dynamic QR codes.
    
    Args:
        short_code (str): The short code to look up
        
    Returns:
        Response: Redirect to the target URL
    """
    qr_code = QRCode.query.filter_by(short_code=short_code, is_active=True).first_or_404()
    QRCodeService.increment_access_count(qr_code)
    return redirect(qr_code.redirect_url or qr_code.url)

@qr_bp.route('/qr/<int:qr_id>/view')
def view_qr_details(qr_id):
    """Display detailed information about a QR code.
    
    Args:
        qr_id (int): ID of the QR code to view
        
    Returns:
        Response: Rendered template with QR code details
    """
    qr_code = QRCode.query.get_or_404(qr_id)
    return render_template('view.html', qr_code=qr_code) 