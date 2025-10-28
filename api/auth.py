"""
Authentication Module for MoMo SMS API
Implements Basic Authentication
"""

import base64
from typing import Optional, Tuple


VALID_CREDENTIALS = {
    "admin": "password123",
    "user": "userpass"
}

def decode_basic_auth(auth_header: str) -> Optional[Tuple[str, str]]:
    """
    Decode Basic Authentication header
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        Tuple of (username, password) or None if invalid
    """
    if not auth_header:
        return None
    
    try:
        if not auth_header.startswith("Basic "):
            return None
        
        encoded = auth_header[6:]  # Remove "Basic "
        decoded = base64.b64decode(encoded).decode('utf-8')
        
        if ':' not in decoded:
            return None
            
        username, password = decoded.split(':', 1)
        return (username, password)
    
    except Exception as e:
        print(f"Error decoding auth: {e}")
        return None

def authenticate(auth_header: str) -> bool:
    """
    Validate credentials against stored users
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        True if authenticated, False otherwise
    """
    credentials = decode_basic_auth(auth_header)
    
    if not credentials:
        return False
    
    username, password = credentials
    
    if username in VALID_CREDENTIALS:
        return VALID_CREDENTIALS[username] == password
    
    return False

def require_auth(handler_func):
    """
    Decorator to protect endpoints with authentication
    Usage: @require_auth above handler methods
    """
    def wrapper(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization', '')
        
        if not authenticate(auth_header):
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
            self.end_headers()
            response = {
                "error": "Unauthorized",
                "message": "Valid credentials required"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # If authenticated, proceed with the handler
        return handler_func(self, *args, **kwargs)
    
    return wrapper