from datetime import datetime
import secrets
from . import db

class QRCode(db.Model):
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    fill_color = db.Column(db.String(50), default='red')
    back_color = db.Column(db.String(50), default='white')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(500))
    access_count = db.Column(db.Integer, default=0)
    is_dynamic = db.Column(db.Boolean, default=False)
    short_code = db.Column(db.String(16), unique=True)

    def __init__(self, **kwargs):
        super(QRCode, self).__init__(**kwargs)
        if self.is_dynamic and not self.short_code:
            self.short_code = self.generate_short_code()

    def generate_short_code(self):
        while True:
            code = secrets.token_urlsafe(8)[:8]
            if not QRCode.query.filter_by(short_code=code).first():
                return code

    def __repr__(self):
        return f'<QRCode {self.id}: {self.url}>' 