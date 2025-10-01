"""
REST API for SMS Transactions
Built with Python http.server
Implements CRUD operations with Basic Authentication
"""

import json
import base64
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional
import sys
import os

# Add parent directory to path to import from dsa folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dsa.xml_parser import load_json_data, save_json_data


class SMSAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for SMS API"""
    
    def __init__(self, *args, **kwargs):
        # Load transaction data
        self.data_file = "sms_data.json"
        self.transactions = self.load_transactions()
        super().__init__(*args, **kwargs)
    
    def load_transactions(self) -> list:
        """Load transactions from JSON file"""
        try:
            return load_json_data(self.data_file)
        except:
            return []
    
    def save_transactions(self):
        """Save transactions to JSON file"""
        save_json_data(self.transactions, self.data_file)
    
    def authenticate(self) -> bool:
        """Check Basic Authentication"""
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return False
        
        try:
            # Decode base64 credentials
            encoded_credentials = auth_header[6:]  # Remove 'Basic '
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)
            
            # Check credentials
            return username == 'admin' and password == 'password'
        except:
            return False
    
    def send_auth_error(self):
        """Send 401 Unauthorized response"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="SMS API"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        error_response = {"error": "Unauthorized", "message": "Invalid credentials"}
        self.wfile.write(json.dumps(error_response).encode())
    
    def send_json_response(self, data: Any, status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def parse_json_body(self) -> Optional[Dict[str, Any]]:
        """Parse JSON from request body"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode('utf-8'))
        except:
            return None
    
    def get_transaction_id_from_path(self) -> Optional[int]:
        """Extract transaction ID from URL path"""
        try:
            path_parts = self.path.split('/')
            if len(path_parts) >= 3 and path_parts[1] == 'transactions':
                return int(path_parts[2])
        except:
            pass
        return None
    
    def do_GET(self):
        """Handle GET requests"""
        if not self.authenticate():
            self.send_auth_error()
            return
        
        if self.path == '/transactions':
            # GET /transactions - List all transactions
            self.send_json_response(self.transactions)
        
        elif self.path.startswith('/transactions/'):
            # GET /transactions/{id} - Get specific transaction
            transaction_id = self.get_transaction_id_from_path()
            if transaction_id is None:
                self.send_json_response({"error": "Invalid transaction ID"}, 400)
                return
            
            # Find transaction by ID
            transaction = None
            for t in self.transactions:
                if t['id'] == transaction_id:
                    transaction = t
                    break
            
            if transaction:
                self.send_json_response(transaction)
            else:
                self.send_json_response({"error": "Transaction not found"}, 404)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        if not self.authenticate():
            self.send_auth_error()
            return
        
        if self.path == '/transactions':
            # POST /transactions - Create new transaction
            new_transaction = self.parse_json_body()
            if not new_transaction:
                self.send_json_response({"error": "Invalid JSON"}, 400)
                return
            
            # Validate required fields
            required_fields = ['sender', 'recipient', 'message', 'timestamp', 'amount', 'status']
            if not all(field in new_transaction for field in required_fields):
                self.send_json_response({"error": "Missing required fields"}, 400)
                return
            
            # Generate new ID
            max_id = max([t['id'] for t in self.transactions]) if self.transactions else 0
            new_transaction['id'] = max_id + 1
            
            # Add transaction
            self.transactions.append(new_transaction)
            self.save_transactions()
            
            self.send_json_response(new_transaction, 201)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_PUT(self):
        """Handle PUT requests"""
        if not self.authenticate():
            self.send_auth_error()
            return
        
        if self.path.startswith('/transactions/'):
            # PUT /transactions/{id} - Update transaction
            transaction_id = self.get_transaction_id_from_path()
            if transaction_id is None:
                self.send_json_response({"error": "Invalid transaction ID"}, 400)
                return
            
            updated_data = self.parse_json_body()
            if not updated_data:
                self.send_json_response({"error": "Invalid JSON"}, 400)
                return
            
            # Find and update transaction
            for i, transaction in enumerate(self.transactions):
                if transaction['id'] == transaction_id:
                    updated_data['id'] = transaction_id  # Preserve ID
                    self.transactions[i] = updated_data
                    self.save_transactions()
                    self.send_json_response(updated_data)
                    return
            
            self.send_json_response({"error": "Transaction not found"}, 404)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        if not self.authenticate():
            self.send_auth_error()
            return
        
        if self.path.startswith('/transactions/'):
            # DELETE /transactions/{id} - Delete transaction
            transaction_id = self.get_transaction_id_from_path()
            if transaction_id is None:
                self.send_json_response({"error": "Invalid transaction ID"}, 400)
                return
            
            # Find and remove transaction
            for i, transaction in enumerate(self.transactions):
                if transaction['id'] == transaction_id:
                    deleted_transaction = self.transactions.pop(i)
                    self.save_transactions()
                    self.send_json_response({"message": "Transaction deleted", "deleted": deleted_transaction})
                    return
            
            self.send_json_response({"error": "Transaction not found"}, 404)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)


def run_server(port: int = 8000):
    """Run the SMS API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SMSAPIHandler)
    print(f"SMS API Server running on port {port}")
    print("Authentication: username='admin', password='password'")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        httpd.server_close()


if __name__ == "__main__":
    run_server()

