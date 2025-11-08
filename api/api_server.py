from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import base64
import os

# Configuration
USERNAME = 'admin'
PASSWORD = 'password123'

# In-memory storage
transactions = []
next_id = 1

def authenticate(auth_header):
    """
    Verify Basic Authentication credentials
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        bool: True if authenticated, False otherwise
    """
    if not auth_header:
        return False
    
    try:
        # Extract credentials from "Basic base64string"
        auth_type, credentials = auth_header.split(' ', 1)
        
        if auth_type.lower() != 'basic':
            return False
        
        # Decode base64
        decoded = base64.b64decode(credentials).decode('utf-8')
        username, password = decoded.split(':', 1)
        
        # Verify credentials
        return username == USERNAME and password == PASSWORD
        
    except Exception:
        return False

def load_transactions_from_xml(filename='modified_sms_v2.xml'):
    """Load transactions from XML file into memory"""
    global transactions, next_id
    
    # Try current directory first, then parent directory
    xml_paths = [
        filename,
        os.path.join('..', filename),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    ]
    
    for xml_path in xml_paths:
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                for trans in root.findall('transaction'):
                    transaction = {
                        'id': trans.get('id'),
                        'type': trans.find('type').text,
                        'amount': float(trans.find('amount').text),
                        'sender': trans.find('sender').text,
                        'receiver': trans.find('receiver').text,
                        'timestamp': trans.find('timestamp').text,
                        'status': trans.find('status').text,
                        'description': trans.find('description').text
                    }
                    transactions.append(transaction)
                
                next_id = len(transactions) + 1
                print(f"✓ Loaded {len(transactions)} transactions from XML")
                return
                
            except Exception as e:
                print(f"Error loading XML from {xml_path}: {e}")
                continue
    
    print(f"⚠ Warning: Could not find {filename} in any expected location")
    print("Server will start with empty dataset")

class APIHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for the MoMo SMS API"""
    
    def _send_cors_headers(self):
        """Send CORS headers for browser compatibility"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def _send_json_response(self, data, status_code=200):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _check_auth(self):
        """Check authentication and return True/False"""
        auth_header = self.headers.get('Authorization', '')
        return authenticate(auth_header)
    
    def _send_unauthorized(self):
        """Send 401 Unauthorized response"""
        self.send_response(401)
        self.send_header('Content-Type', 'application/json')
        self.send_header('WWW-Authenticate', 'Basic realm="MoMo API"')
        self._send_cors_headers()
        self.end_headers()
        response = {
            "error": "Unauthorized",
            "message": "Valid credentials required. Use Basic Authentication.",
            "hint": "Username: admin, Password: password123"
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        # Check authentication
        if not self._check_auth():
            self._send_unauthorized()
            return
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # GET /transactions - List all
        if path == '/transactions':
            self._send_json_response({
                "success": True,
                "count": len(transactions),
                "data": transactions
            })
        
        # GET /transactions/{id} - Get one
        elif path.startswith('/transactions/'):
            trans_id = path.split('/')[-1]
            transaction = next((t for t in transactions if t['id'] == trans_id), None)
            
            if transaction:
                self._send_json_response({
                    "success": True,
                    "data": transaction
                })
            else:
                self._send_json_response({
                    "error": "Not Found",
                    "message": f"Transaction with id '{trans_id}' not found"
                }, 404)
        
        else:
            self._send_json_response({
                "error": "Not Found",
                "message": f"Endpoint '{path}' not found"
            }, 404)
    
    def do_POST(self):
        """Handle POST requests - Create new transaction"""
        # Check authentication
        if not self._check_auth():
            self._send_unauthorized()
            return
        
        if self.path == '/transactions':
            try:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode())
                
                # Validate required fields
                required = ['type', 'amount', 'sender', 'receiver', 'description']
                missing = [f for f in required if f not in data]
                
                if missing:
                    self._send_json_response({
                        "error": "Bad Request",
                        "message": f"Missing required fields: {', '.join(missing)}"
                    }, 400)
                    return
                
                # Create new transaction
                global next_id
                new_transaction = {
                    'id': str(next_id),
                    'type': data['type'],
                    'amount': float(data['amount']),
                    'sender': data['sender'],
                    'receiver': data['receiver'],
                    'timestamp': data.get('timestamp', '2024-01-27T00:00:00Z'),
                    'status': data.get('status', 'completed'),
                    'description': data['description']
                }
                
                transactions.append(new_transaction)
                next_id += 1
                
                self._send_json_response({
                    "success": True,
                    "message": "Transaction created successfully",
                    "data": new_transaction
                }, 201)
                
            except json.JSONDecodeError:
                self._send_json_response({
                    "error": "Bad Request",
                    "message": "Invalid JSON in request body"
                }, 400)
            except Exception as e:
                self._send_json_response({
                    "error": "Internal Server Error",
                    "message": str(e)
                }, 500)
        else:
            self._send_json_response({
                "error": "Not Found",
                "message": f"Endpoint '{self.path}' not found"
            }, 404)
    
    def do_PUT(self):
        """Handle PUT requests - Update transaction"""
        # Check authentication
        if not self._check_auth():
            self._send_unauthorized()
            return
        
        if self.path.startswith('/transactions/'):
            trans_id = self.path.split('/')[-1]
            
            try:
                # Find transaction
                transaction = next((t for t in transactions if t['id'] == trans_id), None)
                
                if not transaction:
                    self._send_json_response({
                        "error": "Not Found",
                        "message": f"Transaction with id '{trans_id}' not found"
                    }, 404)
                    return
                
                # Read and parse update data
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode())
                
                # Update fields (don't allow ID changes)
                updatable = ['type', 'amount', 'sender', 'receiver', 'timestamp', 'status', 'description']
                for field in updatable:
                    if field in data:
                        if field == 'amount':
                            transaction[field] = float(data[field])
                        else:
                            transaction[field] = data[field]
                
                self._send_json_response({
                    "success": True,
                    "message": "Transaction updated successfully",
                    "data": transaction
                })
                
            except json.JSONDecodeError:
                self._send_json_response({
                    "error": "Bad Request",
                    "message": "Invalid JSON in request body"
                }, 400)
            except Exception as e:
                self._send_json_response({
                    "error": "Internal Server Error",
                    "message": str(e)
                }, 500)
        else:
            self._send_json_response({
                "error": "Not Found",
                "message": f"Endpoint '{self.path}' not found"
            }, 404)
    
    def do_DELETE(self):
        """Handle DELETE requests - Delete transaction"""
        # Check authentication
        if not self._check_auth():
            self._send_unauthorized()
            return
        
        if self.path.startswith('/transactions/'):
            trans_id = self.path.split('/')[-1]
            
            # Find and remove transaction
            transaction = next((t for t in transactions if t['id'] == trans_id), None)
            
            if transaction:
                transactions.remove(transaction)
                self._send_json_response({
                    "success": True,
                    "message": f"Transaction {trans_id} deleted successfully"
                })
            else:
                self._send_json_response({
                    "error": "Not Found",
                    "message": f"Transaction with id '{trans_id}' not found"
                }, 404)
        else:
            self._send_json_response({
                "error": "Not Found",
                "message": f"Endpoint '{self.path}' not found"
            }, 404)
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"{self.address_string()} - {format % args}")

def run_server(port=8000):
    """Start the API server"""
    # Load initial data
    load_transactions_from_xml()
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    
    print(f"\n{'='*60}")
    print(f"🚀 MoMo SMS API Server Started")
    print(f"{'='*60}")
    print(f"Server running on: http://localhost:{port}")
    print(f"\nEndpoints:")
    print(f"  GET    /transactions       - List all transactions")
    print(f"  GET    /transactions/{{id}}  - Get single transaction")
    print(f"  POST   /transactions       - Create new transaction")
    print(f"  PUT    /transactions/{{id}}  - Update transaction")
    print(f"  DELETE /transactions/{{id}}  - Delete transaction")
    print(f"\nAuthentication:")
    print(f"  Username: {USERNAME}")
    print(f"  Password: {PASSWORD}")
    print(f"\nPress Ctrl+C to stop the server")
    print(f"{'='*60}\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    run_server()