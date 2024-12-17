"""Service module for handling LLM interactions with the QR code system.

This module provides integration between Groq's LLM API and the QR code application,
enabling natural language interactions with the system's functionality.
"""

import os
import json
import requests
from flask import current_app, url_for
from typing import Dict, Any, List
from ..models.qr_code import QRCode
from ..models import db

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
        }
    }
    
    def __init__(self):
        """Initialize the LLM service with API configuration."""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
            
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.getenv('GROQ_MODEL', 'mixtral-8x7b-32768')
        current_app.logger.info(f"LLM Service initialized with model: {self.model}")
        
    def process_user_request(self, user_input: str) -> dict:
        """Process a user request through the LLM with function calling."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a QR code assistant that helps users manage QR codes. 
                        You can create, list, and delete QR codes through function calls. 
                        Always use the provided functions for operations."""
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                "functions": list(self.AVAILABLE_FUNCTIONS.values()),
                "function_call": "auto",
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 1
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Handle function calling response
            message = result['choices'][0]['message']
            if 'function_call' in message:
                function_call = message['function_call']
                function_name = function_call['name']
                function_args = json.loads(function_call['arguments'])
                
                # Execute the function
                if function_name in self.AVAILABLE_FUNCTIONS:
                    result = self._execute_function(function_name, function_args)
                    return {
                        "success": True,
                        "response": f"I've {function_name.replace('_', ' ')} with the following details: {json.dumps(result, indent=2)}",
                        "function_call": {
                            "name": function_name,
                            "result": result
                        }
                    }
            
            return {
                "success": True,
                "response": message['content']
            }
            
        except Exception as e:
            current_app.logger.error(f"LLM error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error processing your request."
            }
    
    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the requested function with given arguments."""
        from app.services.qr_service import QRCodeService
        qr_service = QRCodeService()
        
        if function_name == "create_qr_code":
            qr_code, path = qr_service.create_qr_code(
                url=args["url"],
                is_dynamic=args.get("is_dynamic", False),
                fill_color=args.get("fill_color", "red"),
                back_color=args.get("back_color", "white"),
                description=args.get("description", ""),
                qr_code_dir=current_app.config['QR_CODE_DIR']
            )
            # Generate QR code image
            qr_url = args["url"]
            if qr_code.is_dynamic:
                qr_url = url_for('qr.redirect_qr', short_code=qr_code.short_code, _external=True)
            qr_service.generate_qr_image(qr_url, path, qr_code.fill_color, qr_code.back_color)
            
            return {
                "qr_code_id": qr_code.id,
                "filename": qr_code.filename,
                "url": qr_code.url
            }
            
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
            
        raise ValueError(f"Unknown function: {function_name}")