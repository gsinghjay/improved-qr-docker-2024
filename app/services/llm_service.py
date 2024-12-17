"""Service module for handling LLM interactions with the QR code system.

This module provides integration between Groq's LLM API and the QR code application,
enabling natural language interactions with the system's functionality.
"""

import os
import json
import requests
from typing import Dict, Any, Optional
from ..models.qr_code import QRCode
from ..services.qr_service import QRCodeService
from flask import current_app

class LLMService:
    """Service class for handling LLM-based interactions."""
    
    def __init__(self):
        """Initialize the LLM service with API configuration."""
        self.api_key = os.getenv('GROQ_API_KEY')
        self.api_url = "https://api.groq.com/v1/chat/completions"
        self.model = "llama3-8b-8192"
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

    def _make_api_request(self, messages: list) -> Dict[str, Any]:
        """Make a request to the Groq API.
        
        Args:
            messages (list): List of message dictionaries for the conversation
            
        Returns:
            dict: The API response
            
        Raises:
            requests.RequestException: If the API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """Process a natural language request and execute corresponding QR code operations.
        
        Args:
            user_input (str): Natural language request from the user
            
        Returns:
            dict: Result of the operation including success status and response
        """
        try:
            # Create system message defining available functions
            system_message = {
                "role": "system",
                "content": """You are a QR code management assistant. You can help with the following operations:
                1. Create new QR codes
                2. List existing QR codes
                3. Update QR code properties
                4. Delete QR codes
                5. Get QR code statistics
                
                Parse the user's request and respond with the appropriate function call."""
            }
            
            # Add user's request
            messages = [
                system_message,
                {"role": "user", "content": user_input}
            ]
            
            # Get LLM response
            response = self._make_api_request(messages)
            
            # Extract the assistant's response
            assistant_response = response['choices'][0]['message']['content']
            
            # Parse the response and execute corresponding function
            return self._execute_qr_operation(assistant_response, user_input)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "Sorry, I encountered an error processing your request."
            }

    def _execute_qr_operation(self, llm_response: str, original_request: str) -> Dict[str, Any]:
        """Execute the QR code operation based on LLM response.
        
        Args:
            llm_response (str): The LLM's interpreted response
            original_request (str): The original user request
            
        Returns:
            dict: Result of the operation
        """
        try:
            # Create new QR code
            if "create" in llm_response.lower() and "qr" in llm_response.lower():
                # Extract URL and other parameters from the response
                params = self._extract_qr_parameters(llm_response)
                
                qr_code, path = QRCodeService.create_qr_code(
                    url=params.get('url', ''),
                    is_dynamic=params.get('is_dynamic', False),
                    fill_color=params.get('fill_color', 'black'),
                    back_color=params.get('back_color', 'white'),
                    description=params.get('description', ''),
                    qr_code_dir=current_app.config['QR_CODE_DIR']
                )
                
                return {
                    "success": True,
                    "response": f"Created new QR code for URL: {qr_code.url}",
                    "qr_code_id": qr_code.id
                }
                
            # List QR codes
            elif "list" in llm_response.lower() or "show" in llm_response.lower():
                qr_codes = QRCode.query.order_by(QRCode.created_at.desc()).all()
                return {
                    "success": True,
                    "response": f"Found {len(qr_codes)} QR codes",
                    "qr_codes": [{"id": qr.id, "url": qr.url, "created_at": qr.created_at} for qr in qr_codes]
                }
                
            # Delete QR code
            elif "delete" in llm_response.lower():
                qr_id = self._extract_qr_id(llm_response)
                qr_code = QRCode.query.get(qr_id)
                
                if qr_code:
                    QRCodeService.delete_qr_code(qr_code, current_app.config['QR_CODE_DIR'])
                    return {
                        "success": True,
                        "response": f"Deleted QR code {qr_id}"
                    }
                else:
                    return {
                        "success": False,
                        "response": f"QR code {qr_id} not found"
                    }
                    
            else:
                return {
                    "success": False,
                    "response": "I'm not sure how to handle that request. Please try rephrasing it."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "Error executing QR code operation"
            }

    def _extract_qr_parameters(self, llm_response: str) -> Dict[str, Any]:
        """Extract QR code parameters from LLM response.
        
        Args:
            llm_response (str): The LLM's response to parse
            
        Returns:
            dict: Extracted parameters for QR code creation
        """
        # Add another message to get structured parameters
        messages = [
            {"role": "system", "content": "Extract QR code parameters from the following text and return them in JSON format with url, is_dynamic, fill_color, back_color, and description fields."},
            {"role": "user", "content": llm_response}
        ]
        
        response = self._make_api_request(messages)
        try:
            # Try to parse JSON from the response
            params_str = response['choices'][0]['message']['content']
            return json.loads(params_str)
        except:
            # Fallback to basic URL extraction if JSON parsing fails
            import re
            url_match = re.search(r'https?://\S+', llm_response)
            return {
                "url": url_match.group(0) if url_match else "",
                "is_dynamic": False,
                "fill_color": "black",
                "back_color": "white",
                "description": ""
            }

    def _extract_qr_id(self, llm_response: str) -> Optional[int]:
        """Extract QR code ID from LLM response.
        
        Args:
            llm_response (str): The LLM's response to parse
            
        Returns:
            Optional[int]: Extracted QR code ID if found
        """
        import re
        id_match = re.search(r'(?:id|ID|#)\s*(\d+)', llm_response)
        return int(id_match.group(1)) if id_match else None 