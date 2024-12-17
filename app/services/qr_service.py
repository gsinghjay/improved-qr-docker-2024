from pathlib import Path
from datetime import datetime
from ..models.qr_code import QRCode
from ..models import db
from ..utils.qr_generator import generate_qr_code, is_valid_url

class QRCodeService:
    @staticmethod
    def create_qr_code(url, is_dynamic, fill_color, back_color, description, qr_code_dir):
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
        path = Path(qr_code_dir) / qr_code.filename
        if path.exists():
            path.unlink()
            
        db.session.delete(qr_code)
        db.session.commit()

    @staticmethod
    def increment_access_count(qr_code):
        qr_code.access_count += 1
        db.session.commit()

    @staticmethod
    def validate_url(url):
        return is_valid_url(url)

    @staticmethod
    def generate_qr_image(url, path, fill_color, back_color):
        return generate_qr_code(url, path, fill_color, back_color) 