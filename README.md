# QR Code Generator with Docker

A Flask-based QR code generator that creates customizable QR codes for URLs. Built with Python, Flask, and Docker, following clean architecture principles.

## Features

- Generate QR codes from URLs
- Customize QR code colors
- Support for both static and dynamic QR codes
- Store QR code history in PostgreSQL database
- Modern web interface with Bootstrap
- Docker containerization for easy deployment
- Clean architecture with MVC pattern

## Architecture

The application follows the Model-View-Controller (MVC) pattern with additional service layer:

```
app/
├── models/              # Data models and database interactions
│   ├── __init__.py     # Database initialization
│   └── qr_code.py      # QR code model
├── controllers/         # Request handling and routing
│   └── qr_controller.py # QR code controller with routes
├── services/           # Business logic layer
│   └── qr_service.py   # QR code service
├── templates/          # View templates
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   ├── edit.html      # Edit QR code
│   └── view.html      # View QR code details
├── utils/             # Utility functions
│   └── qr_generator.py # QR code generation utilities
└── __init__.py        # Application factory
```

## Development

### Prerequisites
- Docker and Docker Compose
- Python 3.12
- Git

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd qr-code-generator

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Docker Setup
```bash
# Build and run services
docker-compose up --build

# Access application
# Web UI: http://localhost:5000
# PgAdmin: http://localhost:5050 (admin@admin.com / admin)
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `QR_CODE_DIR` - Directory for QR code storage
- `FILL_COLOR` - Default QR code fill color
- `BACK_COLOR` - Default QR code background color
- `FLASK_ENV` - Flask environment (development/production)
- `SECRET_KEY` - Flask secret key for sessions

## API Endpoints

- `GET /` - Home page with QR code generation form
- `POST /generate` - Generate new QR code
- `GET /qr/<id>/view` - View QR code details
- `GET /qr/<id>/edit` - Edit QR code form
- `POST /qr/<id>/edit` - Update QR code
- `POST /qr/<id>/delete` - Delete QR code
- `GET /r/<short_code>` - Redirect from dynamic QR code
- `GET /qr_codes/<filename>` - Serve QR code image

## Clean Architecture

The project follows clean architecture principles:

1. **Models**: Handle data structure and database operations
2. **Views**: Handle presentation logic using Jinja2 templates
3. **Controllers**: Handle HTTP requests and routing
4. **Services**: Contain business logic and orchestrate operations
5. **Utils**: Provide helper functions and utilities

## Contributing

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit using conventional commits
git add .
git commit -m "feat(scope): description"
git commit -m "fix(scope): description"
git commit -m "docs(scope): description"

# Push changes
git push origin feature/your-feature

# Create pull request on GitHub
```

### Conventional Commits

We follow conventional commits for clear change history:

- `feat(scope):` New features
- `fix(scope):` Bug fixes
- `docs(scope):` Documentation changes
- `style(scope):` Code style changes
- `refactor(scope):` Code refactoring
- `test(scope):` Test changes
- `chore(scope):` Maintenance tasks

## License

MIT License

## Author

[Your Name]

## Acknowledgments

- Flask framework
- QRCode library
- Docker and Docker Compose
- PostgreSQL database
- Bootstrap for UI
```

