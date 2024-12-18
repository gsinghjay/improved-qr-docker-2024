"""Service module for handling LLM interactions with the QR code system.

This module provides integration between Groq's LLM API and the QR code application,
enabling natural language interactions with the system's functionality.
"""

import os
import json
import requests
import time
from flask import current_app, url_for
from typing import Dict, Any, List, Optional
from ..models.qr_code import QRCode
from ..models import db
from sqlalchemy import desc
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from urllib.parse import urlparse, urljoin
import validators

class LLMService:
    """Service for handling LLM operations using Groq API."""
    
    # Define available functions for QR operations
    AVAILABLE_FUNCTIONS = {
        "create_qr_code": {
            "name": "create_qr_code",
            "description": "Create a new QR code",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to encode in the QR code"
                    },
                    "is_dynamic": {
                        "type": "boolean",
                        "description": "Whether to create a dynamic QR code"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the QR code"
                    },
                    "fill_color": {
                        "type": "string",
                        "description": "Color for QR code fill (e.g., '#000000')"
                    },
                    "back_color": {
                        "type": "string",
                        "description": "Color for QR code background (e.g., '#FFFFFF')"
                    }
                },
                "required": ["url"]
            }
        },
        "list_qr_codes": {
            "name": "list_qr_codes",
            "description": "List all QR codes",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        "delete_qr_code": {
            "name": "delete_qr_code",
            "description": "Delete a QR code by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "qr_id": {
                        "type": "integer",
                        "description": "ID of the QR code to delete"
                    }
                },
                "required": ["qr_id"]
            }
        },
        "search_qr_codes": {
            "name": "search_qr_codes",
            "description": "Search QR codes by various criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Filter by URL (partial match)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Filter by description (partial match)"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Filter by active status"
                    },
                    "created_after": {
                        "type": "string",
                        "description": "Filter by creation date (ISO format)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return"
                    }
                }
            }
        },
        "update_qr_code": {
            "name": "update_qr_code",
            "description": "Update an existing QR code",
            "parameters": {
                "type": "object",
                "properties": {
                    "qr_id": {
                        "type": "integer",
                        "description": "ID of the QR code to update"
                    },
                    "url": {
                        "type": "string",
                        "description": "New URL for the QR code"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description"
                    },
                    "is_active": {
                        "type": "boolean",
                        "description": "Set active status"
                    },
                    "fill_color": {
                        "type": "string",
                        "description": "New fill color"
                    },
                    "back_color": {
                        "type": "string",
                        "description": "New background color"
                    }
                },
                "required": ["qr_id"]
            }
        }
    }
    
    def __init__(self):
        """Initialize the LLM service with API configuration."""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
            
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        self.rate_limit_delay = 1.0  # Seconds between API calls
        self._last_api_call = 0
        current_app.logger.info(f"LLM Service initialized with model: {self.model}")
        
    def _rate_limit(self):
        """Implement rate limiting for API calls."""
        now = time.time()
        time_since_last_call = now - self._last_api_call
        if time_since_last_call < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_call)
        self._last_api_call = time.time()

    @lru_cache(maxsize=100)
    def _get_cached_response(self, user_input: str) -> Optional[Dict]:
        """Get cached response for identical queries."""
        return None  # Cache implementation

    def format_qr_code_response(self, qr_codes: List[Dict]) -> str:
        """Format QR code list for better readability."""
        if not qr_codes:
            return "No QR codes found."
            
        response = "Here are the QR codes:\n\n"
        for qr in qr_codes:
            response += f"📱 QR Code #{qr['id']}\n"
            response += f"🔗 URL: {qr['url']}\n"
            if qr.get('description'):
                response += f"📝 Description: {qr['description']}\n"
            response += f"📅 Created: {qr['created_at']}\n"
            response += f"👁️ Views: {qr.get('access_count', 0)}\n"
            response += "-------------------\n"
        return response

    def format_url(self, url: str) -> str:
        """Format and validate URL to ensure proper structure."""
        if not url:
            raise ValueError("URL cannot be empty")
            
        # Add scheme if missing
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
            
        # Validate URL structure
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid URL format")
            
        # Validate domain
        if not validators.domain(parsed.netloc):
            raise ValueError(f"Invalid domain: {parsed.netloc}")
            
        return url

    def process_user_request(self, user_input: str) -> dict:
        """Process a user request through the LLM with function calling."""
        try:
            # Check cache first
            cached_response = self._get_cached_response(user_input)
            if cached_response:
                return cached_response

            # Apply rate limiting
            self._rate_limit()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            system_prompt = """You are a helpful QR code assistant. You can:
            1. Create new QR codes
            2. List existing QR codes
            3. Search for specific QR codes
            4. Update QR code properties
            5. Delete QR codes

            Always validate URLs and provide clear, friendly responses.
            For errors, explain what went wrong and how to fix it."""

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "functions": list(self.AVAILABLE_FUNCTIONS.values()),
                "function_call": "auto",
                "temperature": 0.7
            }

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:
                    return {
                        "success": False,
                        "response": "I'm receiving too many requests right now. Please try again in a few seconds.",
                        "error": str(e)
                    }
                return {
                    "success": False,
                    "response": "I'm having trouble connecting to my language model. Please try again.",
                    "error": str(e)
                }

            result = response.json()
            message = result['choices'][0]['message']

            if 'function_call' in message:
                function_call = message['function_call']
                function_name = function_call['name']
                function_args = json.loads(function_call['arguments'])

                try:
                    result = self._execute_function(function_name, function_args)
                    
                    # Enhanced response formatting
                    if function_name == 'create_qr_code':
                        response_text = (
                            f"✅ Created QR code #{result['qr_code_id']}\n"
                            f"🔗 URL: {result['url']}\n"
                            f"📁 Filename: {result['filename']}"
                        )
                    elif function_name == 'list_qr_codes':
                        response_text = self.format_qr_code_response(result['qr_codes'])
                    else:
                        response_text = f"I've completed the '{function_name.replace('_', ' ')}' operation successfully."
                    
                    return {
                        "success": True,
                        "response": response_text,
                        "function_call": {
                            "name": function_name,
                            "result": result
                        }
                    }
                    
                except ValueError as ve:
                    return {
                        "success": False,
                        "response": f"⚠️ Error: {str(ve)}. Please try again with a valid URL.",
                        "error": str(ve)
                    }

            return {
                "success": True,
                "response": message['content']
            }

        except Exception as e:
            current_app.logger.error(f"Error processing request: {str(e)}")
            return {
                "success": False,
                "response": "I encountered an unexpected error. Please try again.",
                "error": str(e)
            }
    
    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified function with given arguments."""
        from app.services.qr_service import QRCodeService
        qr_service = QRCodeService()
        
        if function_name == "create_qr_code":
            try:
                # Format and validate URL
                url = self.format_url(args["url"])
                
                qr_code = QRCode(
                    url=url,
                    is_dynamic=args.get("is_dynamic", False),
                    description=args.get("description", ""),
                    fill_color=args.get("fill_color", "#000000"),
                    back_color=args.get("back_color", "#FFFFFF")
                )
                
                db.session.add(qr_code)
                db.session.commit()
                
                # Generate QR code image
                path = Path(current_app.config['QR_CODE_DIR']) / qr_code.filename
                if not QRCodeService.generate_qr_image(
                    qr_code.url,
                    path,
                    qr_code.fill_color,
                    qr_code.back_color
                ):
                    raise ValueError("Failed to generate QR code image")
                
                return {
                    "qr_code_id": qr_code.id,
                    "filename": qr_code.filename,
                    "url": qr_code.url
                }
                
            except Exception as e:
                db.session.rollback()
                raise ValueError(f"Failed to create QR code: {str(e)}")
            
        elif function_name == "list_qr_codes":
            qr_codes = QRCode.query.order_by(QRCode.created_at.desc()).all()
            return {
                "qr_codes": [
                    {
                        "id": qr.id,
                        "url": qr.url,
                        "filename": qr.filename,
                        "created_at": qr.created_at.isoformat(),
                        "access_count": qr.access_count
                    } for qr in qr_codes
                ]
            }
            
        elif function_name == "delete_qr_code":
            qr_code = QRCode.query.get(args["qr_id"])
            if qr_code:
                qr_service.delete_qr_code(qr_code, current_app.config['QR_CODE_DIR'])
                return {"success": True, "message": f"QR code {args['qr_id']} deleted"}
            return {"success": False, "message": f"QR code {args['qr_id']} not found"}
            
        elif function_name == "search_qr_codes":
            query = QRCode.query

            if args.get("url"):
                query = query.filter(QRCode.url.ilike(f"%{args['url']}%"))
            
            if args.get("description"):
                query = query.filter(QRCode.description.ilike(f"%{args['description']}%"))
            
            if "is_active" in args:
                query = query.filter(QRCode.is_active == args["is_active"])
            
            if args.get("created_after"):
                try:
                    date = datetime.fromisoformat(args["created_after"])
                    query = query.filter(QRCode.created_at >= date)
                except ValueError:
                    raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DD)")

            query = query.order_by(desc(QRCode.created_at))
            
            if args.get("limit"):
                query = query.limit(args["limit"])

            qr_codes = query.all()
            
            return {
                "qr_codes": [
                    {
                        "id": qr.id,
                        "url": qr.url,
                        "filename": qr.filename,
                        "description": qr.description,
                        "is_active": qr.is_active,
                        "created_at": qr.created_at.isoformat(),
                        "access_count": qr.access_count
                    } for qr in qr_codes
                ],
                "total_results": len(qr_codes)
            }

        elif function_name == "update_qr_code":
            qr_code = QRCode.query.get(args["qr_id"])
            if not qr_code:
                raise ValueError(f"QR code {args['qr_id']} not found")

            # Update fields if provided
            if "url" in args:
                if not QRCodeService.validate_url(args["url"]):
                    raise ValueError("Invalid URL provided")
                qr_code.url = args["url"]

            if "description" in args:
                qr_code.description = args["description"]

            if "is_active" in args:
                qr_code.is_active = args["is_active"]

            if "fill_color" in args:
                qr_code.fill_color = args["fill_color"]

            if "back_color" in args:
                qr_code.back_color = args["back_color"]

            qr_code.updated_at = datetime.utcnow()
            
            try:
                db.session.commit()
                
                # Regenerate QR code image if URL changed
                if "url" in args:
                    path = Path(current_app.config['QR_CODE_DIR']) / qr_code.filename
                    QRCodeService.generate_qr_image(
                        qr_code.url,
                        path,
                        qr_code.fill_color,
                        qr_code.back_color
                    )

                return {
                    "success": True,
                    "qr_code": {
                        "id": qr_code.id,
                        "url": qr_code.url,
                        "description": qr_code.description,
                        "is_active": qr_code.is_active,
                        "updated_at": qr_code.updated_at.isoformat()
                    }
                }
            except Exception as e:
                db.session.rollback()
                raise ValueError(f"Failed to update QR code: {str(e)}")
            
        raise ValueError(f"Unknown function: {function_name}")