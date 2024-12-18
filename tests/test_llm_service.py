import pytest
from unittest.mock import patch, MagicMock
from app.services.llm_service import LLMService
from app.models.qr_code import QRCode
import os
from datetime import datetime, timezone
import requests

@pytest.fixture
def mock_env():
    """Setup environment variables for testing."""
    with patch.dict(os.environ, {
        'GROQ_API_KEY': 'test_key',
        'GROQ_MODEL': 'mixtral-8x7b-32768'
    }):
        yield

@pytest.fixture
def mock_requests():
    """Mock requests for LLM API calls."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'Test response',
                    'function_call': {
                        'name': 'list_qr_codes',
                        'arguments': '{}'
                    }
                }
            }]
        }
        mock_post.return_value = mock_response
        yield mock_post

@pytest.mark.usefixtures('mock_env')
class TestLLMService:
    def test_initialization(self, app):
        """Test LLM service initialization."""
        with app.app_context():
            service = LLMService()
            assert service.api_key == 'test_key'
            assert service.model == 'mixtral-8x7b-32768'
            assert service.rate_limit_delay == 1.0

    def test_initialization_no_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {'GROQ_API_KEY': ''}, clear=True):
            with pytest.raises(ValueError, match="GROQ_API_KEY environment variable not set"):
                LLMService()

    def test_rate_limit(self, app):
        """Test rate limiting."""
        with app.app_context():
            service = LLMService()
            with patch('time.sleep') as mock_sleep:
                service._rate_limit()
                service._rate_limit()
                mock_sleep.assert_called_once()

    def test_cache_response(self, app):
        """Test response caching."""
        with app.app_context():
            service = LLMService()
            assert service._get_cached_response("test") is None

    def test_format_qr_code_response_empty(self, app):
        """Test QR code response formatting with empty list."""
        with app.app_context():
            service = LLMService()
            assert service.format_qr_code_response([]) == "No QR codes found."

    def test_format_qr_code_response(self, app):
        """Test QR code response formatting with data."""
        with app.app_context():
            service = LLMService()
            qr_codes = [{
                'id': 1,
                'url': 'https://example.com',
                'description': 'Test QR',
                'created_at': '2024-01-01T00:00:00',
                'access_count': 5
            }]
            response = service.format_qr_code_response(qr_codes)
            assert 'QR Code #1' in response
            assert 'https://example.com' in response
            assert 'Test QR' in response

    def test_process_user_request_success(self, mock_requests, app):
        """Test successful user request processing."""
        with app.app_context():
            service = LLMService()
            result = service.process_user_request("List all QR codes")
            assert result['success'] == True
            assert 'response' in result
            mock_requests.assert_called_once()

    def test_process_user_request_api_error(self, app):
        """Test API error handling."""
        with app.app_context(), patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_post.side_effect = requests.exceptions.RequestException("API Error")
            
            service = LLMService()
            result = service.process_user_request("Test message")
            assert result['success'] == False
            assert "trouble connecting" in result['response']

    def test_process_user_request_rate_limit(self, app):
        """Test rate limit error handling."""
        with app.app_context(), patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_post.return_value = mock_response
            
            service = LLMService()
            result = service.process_user_request("Test message")
            assert result['success'] == False
            assert "too many requests" in result['response']

    @pytest.mark.parametrize("function_name,args,expected", [
        ("list_qr_codes", {}, {"qr_codes": []}),
        ("create_qr_code", {"url": "https://example.com"}, 
         {"qr_code_id": 1, "url": "https://example.com"}),
        ("delete_qr_code", {"qr_id": 999}, 
         {"success": False, "message": "QR code 999 not found"}),
    ])
    def test_execute_function(self, app, function_name, args, expected):
        """Test function execution with various inputs."""
        with app.app_context():
            service = LLMService()
            result = service._execute_function(function_name, args)
            for key in expected:
                assert key in result
                if isinstance(expected[key], list):
                    assert isinstance(result[key], list)
                else:
                    assert result[key] == expected[key]

    def test_execute_function_unknown(self, app):
        """Test unknown function handling."""
        with app.app_context():
            service = LLMService()
            with pytest.raises(ValueError, match="Unknown function"):
                service._execute_function("unknown_function", {})

    def test_search_qr_codes(self, app, session):
        """Test QR code search functionality."""
        with app.app_context():
            # Create test QR code
            qr = QRCode(
                url='https://example.com',
                filename='test.png',
                description='Test QR',
                created_at=datetime.now(timezone.utc)
            )
            session.add(qr)
            session.commit()

            service = LLMService()
            result = service._execute_function("search_qr_codes", {
                "url": "example",
                "description": "Test",
                "is_active": True,
                "created_after": datetime.now(timezone.utc).isoformat(),
                "limit": 1
            })
            
            assert "qr_codes" in result
            assert "total_results" in result

    def test_update_qr_code(self, app, session):
        """Test QR code update functionality."""
        with app.app_context():
            # Create test QR code
            qr = QRCode(
                url='https://example.com',
                filename='test.png'
            )
            session.add(qr)
            session.commit()

            service = LLMService()
            result = service._execute_function("update_qr_code", {
                "qr_id": qr.id,
                "url": "https://updated.com",
                "description": "Updated QR"
            })
            
            assert result["success"] == True
            assert result["qr_code"]["url"] == "https://updated.com"