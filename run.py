from app import create_app
from app.utils.qr_generator import setup_logging

app = create_app()

if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=5000, debug=True) 