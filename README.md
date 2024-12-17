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
- LLM-powered chat interface for natural language QR code operations
- Support for multiple LLM models (Mixtral, LLaMA 2, Gemma)
- Persistent chat interface across all pages
- Model selection and configuration UI

Here's the updated architecture section for the README.md, incorporating the testing infrastructure:

## Architecture

The application follows the Model-View-Controller (MVC) pattern with additional service layer, testing infrastructure, and Docker containerization:

```
app/
├── models/              # Data models and database interactions
│   ├── __init__.py     # Database initialization
│   └── qr_code.py      # QR code model
├── controllers/         # Request handling and routing
│   └── qr_controller.py # QR code controller with routes
├── services/           # Business logic layer
│   ├── qr_service.py   # QR code service
│   └── llm_service.py  # LLM integration service
├── templates/          # View templates
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   ├── edit.html      # Edit QR code
│   └── view.html      # View QR code details
├── utils/             # Utility functions
│   └── qr_generator.py # QR code generation utilities
└── __init__.py        # Application factory

project_root/
├── Dockerfile         # Container configuration
├── docker-compose.yml # Multi-container Docker setup
├── logs/             # Application logs directory
│   └── docker_logs.txt # Docker runtime logs
├── qr_codes/         # Generated QR code storage
├── requirements.txt  # Python dependencies
├── run.py           # Application entry point
├── pytest.ini       # Test configuration
└── tests/           # Test suite
    ├── conftest.py  # Test fixtures and configuration
    └── test_qr_controller.py # Controller tests
```

The application is containerized using Docker with four main services:
- **qr_code_app**: Flask application container (Python 3.12)
- **db**: PostgreSQL 15 database container
- **pgadmin**: PostgreSQL administration interface
- **test_app**: Test container for CI/CD pipeline

Key directories:
- **/logs**: Contains application logs, mounted as a Docker volume
- **/qr_codes**: Stores generated QR code images, mounted as a Docker volume
- **/app**: Core application code, mounted for development hot-reloading
- **/tests**: Test suite and fixtures
- **/.github/workflows**: CI/CD configuration

Testing Architecture:
- **conftest.py**: Provides test fixtures and database setup
- **test_qr_controller.py**: Controller tests
- **pytest.ini**: Test discovery and coverage configuration
- **GitHub Actions**: Automated testing pipeline with PostgreSQL service

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

## Testing

### Running Tests Locally
```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests with coverage report
pytest tests/ --cov=app -v

# Run tests without coverage
pytest tests/ -v

# Run specific test file
pytest tests/test_qr_controller.py -v
```

### Test Structure
- `tests/conftest.py`: Test fixtures and configuration
- `tests/test_qr_controller.py`: Controller tests
- `pytest.ini`: Test discovery and configuration

### Coverage Reports
Coverage reports are available when running tests locally:
```bash
# Generate detailed coverage report
pytest tests/ --cov=app --cov-report=term-missing -v
```

This will show:
- Percentage of code covered by tests
- Lines that are not covered
- Module-by-module breakdown of coverage

### GitHub Actions CI
The project includes automated testing via GitHub Actions:
- Runs on every push and pull request
- Uses PostgreSQL service container
- Executes the full test suite
- Validates code functionality across different environments

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `QR_CODE_DIR` - Directory for QR code storage
- `FILL_COLOR` - Default QR code fill color
- `BACK_COLOR` - Default QR code background color
- `FLASK_ENV` - Flask environment (development/production)
- `SECRET_KEY` - Flask secret key for sessions
- `GROQ_API_KEY` - API key for Groq LLM service
- `GROQ_MODEL` - Selected LLM model (mixtral-8x7b-32768, llama2-70b-4096, or gemma-7b-it)

## API Endpoints

- `GET /` - Home page with QR code generation form
- `POST /generate` - Generate new QR code
- `GET /qr/<id>/view` - View QR code details
- `GET /qr/<id>/edit` - Edit QR code form
- `POST /qr/<id>/edit` - Update QR code
- `POST /qr/<id>/delete` - Delete QR code
- `GET /r/<short_code>` - Redirect from dynamic QR code
- `GET /qr_codes/<filename>` - Serve QR code image
- `POST /chat` - Process natural language requests
- `POST /update_model` - Update LLM model selection

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

## Acknowledgments

- Flask framework
- QRCode library
- Docker and Docker Compose
- PostgreSQL database
- Bootstrap for UI

## LLM Integration

### Available Models

1. **Mixtral 8x7B**
   - 32K context window
   - Recommended for general use
   - Best balance of performance and speed

2. **LLaMA 2 70B**
   - 4K context window
   - Highest accuracy
   - More computational resources

3. **Gemma 7B**
   - Lightweight model
   - Fast response times
   - Good for basic operations

### Chat Interface

The application includes a persistent chat interface that allows:
- Natural language QR code generation
- QR code management through conversation
- Model selection and configuration
- Status feedback and error handling

### Example Commands

```
"Create a QR code for https://example.com"
"Make a dynamic QR code with red fill color"
"Show me all QR codes"
"Delete QR code #5"
"Update QR code description"
```
```

