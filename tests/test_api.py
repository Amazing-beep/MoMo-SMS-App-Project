
import requests
import json
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://localhost:8000"
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"
INVALID_USERNAME = "wrong"
INVALID_PASSWORD = "credentials"

class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEST: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*70}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

def print_response(response):
    """Print formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    try:
        print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Body:\n{response.text}")

def test_get_all_transactions():
    """Test GET /transactions with valid credentials"""
    print_test_header("GET All Transactions (Authenticated)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/transactions",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD)
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                print_success(f"Successfully retrieved {data.get('count', 0)} transactions")
                return True
            else:
                print_error("Response format is incorrect")
                return False
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_get_transaction_by_id():
    """Test GET /transactions/{id} with valid credentials"""
    print_test_header("GET Transaction by ID (Authenticated)")
    
    transaction_id = "1"
    
    try:
        response = requests.get(
            f"{BASE_URL}/transactions/{transaction_id}",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD)
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                print_success(f"Successfully retrieved transaction {transaction_id}")
                return True
            else:
                print_error("Response format is incorrect")
                return False
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_unauthorized_access():
    """Test GET /transactions with invalid credentials"""
    print_test_header("Unauthorized Access Test (Invalid Credentials)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/transactions",
            auth=HTTPBasicAuth(INVALID_USERNAME, INVALID_PASSWORD)
        )
        
        print_response(response)
        
        if response.status_code == 401:
            print_success("Correctly rejected invalid credentials with 401")
            return True
        else:
            print_error(f"Expected status 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_no_authentication():
    """Test GET /transactions without credentials"""
    print_test_header("No Authentication Test")
    
    try:
        response = requests.get(f"{BASE_URL}/transactions")
        
        print_response(response)
        
        if response.status_code == 401:
            print_success("Correctly rejected request without credentials with 401")
            return True
        else:
            print_error(f"Expected status 401, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_create_transaction():
    """Test POST /transactions"""
    print_test_header("Create New Transaction (POST)")
    
    new_transaction = {
        "type": "payment",
        "amount": 125.50,
        "sender": "+1111111111",
        "receiver": "+2222222222",
        "description": "Test payment from automated script",
        "timestamp": "2024-01-27T12:00:00Z"
    }
    
    print_info(f"Creating transaction: {json.dumps(new_transaction, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/transactions",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD),
            headers={"Content-Type": "application/json"},
            json=new_transaction
        )
        
        print_response(response)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success') and 'data' in data:
                created_id = data['data'].get('id')
                print_success(f"Successfully created transaction with ID: {created_id}")
                return created_id
            else:
                print_error("Response format is incorrect")
                return None
        else:
            print_error(f"Expected status 201, got {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return None

def test_update_transaction(transaction_id):
    """Test PUT /transactions/{id}"""
    print_test_header(f"Update Transaction (PUT) - ID: {transaction_id}")
    
    update_data = {
        "amount": 200.00,
        "description": "Updated test payment"
    }
    
    print_info(f"Updating with: {json.dumps(update_data, indent=2)}")
    
    try:
        response = requests.put(
            f"{BASE_URL}/transactions/{transaction_id}",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD),
            headers={"Content-Type": "application/json"},
            json=update_data
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success(f"Successfully updated transaction {transaction_id}")
                return True
            else:
                print_error("Response format is incorrect")
                return False
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_delete_transaction(transaction_id):
    """Test DELETE /transactions/{id}"""
    print_test_header(f"Delete Transaction (DELETE) - ID: {transaction_id}")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/transactions/{transaction_id}",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD)
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success(f"Successfully deleted transaction {transaction_id}")
                return True
            else:
                print_error("Response format is incorrect")
                return False
        else:
            print_error(f"Expected status 200, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_get_nonexistent_transaction():
    """Test GET /transactions/{id} with non-existent ID"""
    print_test_header("GET Non-existent Transaction (404 Test)")
    
    transaction_id = "99999"
    
    try:
        response = requests.get(
            f"{BASE_URL}/transactions/{transaction_id}",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD)
        )
        
        print_response(response)
        
        if response.status_code == 404:
            print_success("Correctly returned 404 for non-existent transaction")
            return True
        else:
            print_error(f"Expected status 404, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def test_create_invalid_transaction():
    """Test POST with missing required fields"""
    print_test_header("Create Transaction with Missing Fields (400 Test)")
    
    invalid_transaction = {
        "type": "payment",
        "sender": "+1111111111"
        # Missing: amount, receiver, description
    }
    
    print_info(f"Sending invalid data: {json.dumps(invalid_transaction, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/transactions",
            auth=HTTPBasicAuth(VALID_USERNAME, VALID_PASSWORD),
            headers={"Content-Type": "application/json"},
            json=invalid_transaction
        )
        
        print_response(response)
        
        if response.status_code == 400:
            print_success("Correctly rejected invalid data with 400")
            return True
        else:
            print_error(f"Expected status 400, got {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Request failed: {str(e)}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print(f"\n{Colors.BOLD}{'='*70}")
    print("MoMo SMS Transaction API - Automated Test Suite")
    print(f"{'='*70}{Colors.END}\n")
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Valid credentials: {VALID_USERNAME}/{VALID_PASSWORD}")
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test 1: Get all transactions (authenticated)
    results["total"] += 1
    if test_get_all_transactions():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 2: Get transaction by ID
    results["total"] += 1
    if test_get_transaction_by_id():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Unauthorized access
    results["total"] += 1
    if test_unauthorized_access():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 4: No authentication
    results["total"] += 1
    if test_no_authentication():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Create transaction
    results["total"] += 1
    created_id = test_create_transaction()
    if created_id:
        results["passed"] += 1
        
        # Test 6: Update the created transaction
        results["total"] += 1
        if test_update_transaction(created_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 7: Delete the created transaction
        results["total"] += 1
        if test_delete_transaction(created_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        results["failed"] += 1
        results["total"] += 2  # Skip update and delete tests
        print_info("Skipping update and delete tests due to failed creation")
    
    # Test 8: Get non-existent transaction
    results["total"] += 1
    if test_get_nonexistent_transaction():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 9: Create invalid transaction
    results["total"] += 1
    if test_create_invalid_transaction():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}{Colors.END}")
    print(f"Total Tests: {results['total']}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    
    if results['failed'] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Some tests failed. Please review the output above.{Colors.END}")
    
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}ERROR: Could not connect to API server at {BASE_URL}{Colors.END}")
        print(f"{Colors.YELLOW}Please ensure the API server is running before running tests.{Colors.END}")
        print(f"{Colors.YELLOW}Start the server with: python api_server.py{Colors.END}\n")