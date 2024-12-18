"""Controller module for handling QR code-related HTTP requests.

This module defines the routes and request handling logic for the QR code
generation and management system.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from ..models.qr_code import QRCode
from ..services.qr_service import QRCodeService
from ..services.llm_service import LLMService
from flask import current_app
import os
import requests

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
def view_qr(qr_id):
    qr_code = QRCode.query.get_or_404(qr_id)
    
    # Check if GROQ_API_KEY exists and is not empty
    groq_enabled = bool(os.getenv('GROQ_API_KEY'))
    current_model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
    
    return render_template('view.html', 
                         qr_code=qr_code, 
                         groq_enabled=groq_enabled,
                         current_model=current_model)

@qr_bp.route('/chat', methods=['POST'])
def chat():
    """Handle natural language chat requests for QR code operations."""
    try:
        user_input = request.json.get('message')
        current_app.logger.info(f"Received chat message: {user_input}")
        
        if not user_input:
            current_app.logger.warning("No message provided")
            return jsonify({
                "success": False,
                "response": "No message provided"
            }), 400
            
        # Check if Groq API is configured
        if not os.getenv('GROQ_API_KEY'):
            current_app.logger.error("GROQ_API_KEY not configured")
            return jsonify({
                "success": False,
                "response": "LLM service is not configured. Please set GROQ_API_KEY in environment variables."
            }), 503
            
        try:
            llm_service = LLMService()
            current_app.logger.info("Processing message with LLM service")
            result = llm_service.process_user_request(user_input)
            current_app.logger.info(f"LLM response: {result}")
            return jsonify(result)
            
        except ValueError as ve:
            current_app.logger.error(f"LLM configuration error: {str(ve)}")
            return jsonify({
                "success": False,
                "response": f"LLM service configuration error: {str(ve)}"
            }), 503
            
        except requests.RequestException as re:
            current_app.logger.error(f"Groq API error: {str(re)}")
            return jsonify({
                "success": False,
                "response": "Unable to connect to LLM service. Please try again later."
            }), 503
            
    except Exception as e:
        current_app.logger.error(f"Unexpected chat error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "An unexpected error occurred. Please try again."
        }), 500

@qr_bp.route('/update_model', methods=['POST'])
def update_model():
    """Update the LLM model selection.
    
    Returns:
        Response: JSON response indicating success/failure
    """
    try:
        model = request.json.get('model')
        if not model:
            return jsonify({
                'success': False,
                'error': 'No model specified'
            }), 400
            
        # Validate model selection
        valid_models = ['mixtral-8x7b-32768', 'llama2-70b-4096', 'gemma-7b-it']
        if model not in valid_models:
            return jsonify({
                'success': False,
                'error': 'Invalid model selection'
            }), 400
            
        # Update model in environment
        os.environ['GROQ_MODEL'] = model
        
        return jsonify({
            'success': True,
            'model': model
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 