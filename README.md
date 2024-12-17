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

## Prerequisites

1. Docker and Docker Compose
2. Git

## Quick Start

1. Clone the repository:
```bash
git clone <your-repo-url>
cd qr-code-generator
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
- QR Code Generator: http://localhost:5000
- PgAdmin: http://localhost:5050 (admin@admin.com / admin)

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

## Development

The project follows clean architecture principles:

1. **Models**: Handle data structure and database operations
2. **Views**: Handle presentation logic using Jinja2 templates
3. **Controllers**: Handle HTTP requests and routing
4. **Services**: Contain business logic and orchestrate operations
5. **Utils**: Provide helper functions and utilities

## Contributing

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes following conventional commits:
```bash
git commit -m "feat(scope): description"
git commit -m "fix(scope): description"
git commit -m "chore(scope): description"
```

3. Push changes:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request

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

4. Add and commit the updated readme:
```bash
git add README.md
git commit -m "docs: Update README with comprehensive documentation"
```

5. Create a new branch for development:
```bash
git checkout -b develop
```

6. Set up remote repository (replace with your GitHub URL):
```bash
git remote add origin https://github.com/yourusername/qr-code-generator.git
git push -u origin main
git push -u origin develop
```

