"""
Test script for the Transaction API
Demonstrates all CRUD operations and authentication
"""

import requests
import json
import base64
from requests.auth import HTTPBasicAuth

# API Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "password123"

def test_authentication():
    """Test API authentication"""
    print("=== Testing Authentication ===")
    
    # Test with valid credentials
    try:
        response = requests.get(f"{BASE_URL}/transactions", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        if response.status_code == 200:
            print("✓ Valid credentials work")
        else:
            print(f"✗ Valid credentials failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server. Make sure it's running on port 8000")
        return False
    
    # Test with invalid credentials
    response = requests.get(f"{BASE_URL}/transactions", auth=HTTPBasicAuth("wrong", "credentials"))
    if response.status_code == 401:
        print("✓ Invalid credentials properly rejected")
    else:
        print(f"✗ Invalid credentials not rejected: {response.status_code}")
    
    # Test without credentials
    response = requests.get(f"{BASE_URL}/transactions")
    if response.status_code == 401:
        print("✓ Missing credentials properly rejected")
    else:
        print(f"✗ Missing credentials not rejected: {response.status_code}")
    
    return True

def test_get_all_transactions():
    """Test GET /transactions"""
    print("\n=== Testing GET /transactions ===")
    
    response = requests.get(f"{BASE_URL}/transactions", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {data['count']} transactions")
        if data['transactions']:
            print(f"  Sample transaction: {data['transactions'][0]['type']} - ${data['transactions'][0]['amount']}")
    else:
        print(f"✗ Failed to get transactions: {response.status_code}")

def test_get_transaction_by_id():
    """Test GET /transactions/{id}"""
    print("\n=== Testing GET /transactions/{id} ===")
    
    # First get all transactions to find a valid ID
    response = requests.get(f"{BASE_URL}/transactions", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        data = response.json()
        if data['transactions']:
            transaction_id = data['transactions'][0]['id']
            
            # Test getting specific transaction
            response = requests.get(f"{BASE_URL}/transactions/{transaction_id}", auth=HTTPBasicAuth(USERNAME, PASSWORD))
            if response.status_code == 200:
                transaction = response.json()
                print(f"✓ Retrieved transaction {transaction_id}: {transaction['type']} - ${transaction['amount']}")
            else:
                print(f"✗ Failed to get transaction {transaction_id}: {response.status_code}")
        else:
            print("✗ No transactions available for testing")
    else:
        print("✗ Cannot get transactions list")

def test_create_transaction():
    """Test POST /transactions"""
    print("\n=== Testing POST /transactions ===")
    
    new_transaction = {
        "type": "transfer",
        "amount": 99.99,
        "sender": "+1111111111",
        "receiver": "+2222222222",
        "description": "Test API transaction"
    }
    
    response = requests.post(
        f"{BASE_URL}/transactions",
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        json=new_transaction,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        created_transaction = response.json()
        print(f"✓ Created transaction {created_transaction['id']}: {created_transaction['type']} - ${created_transaction['amount']}")
        return created_transaction['id']
    else:
        print(f"✗ Failed to create transaction: {response.status_code} - {response.text}")
        return None

def test_update_transaction(transaction_id):
    """Test PUT /transactions/{id}"""
    print(f"\n=== Testing PUT /transactions/{transaction_id} ===")
    
    if not transaction_id:
        print("✗ No transaction ID provided for update test")
        return
    
    update_data = {
        "amount": 199.99,
        "description": "Updated test transaction"
    }
    
    response = requests.put(
        f"{BASE_URL}/transactions/{transaction_id}",
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        json=update_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        updated_transaction = response.json()
        print(f"✓ Updated transaction {transaction_id}: ${updated_transaction['amount']} - {updated_transaction['description']}")
    else:
        print(f"✗ Failed to update transaction: {response.status_code} - {response.text}")

def test_delete_transaction(transaction_id):
    """Test DELETE /transactions/{id}"""
    print(f"\n=== Testing DELETE /transactions/{transaction_id} ===")
    
    if not transaction_id:
        print("✗ No transaction ID provided for delete test")
        return
    
    response = requests.delete(
        f"{BASE_URL}/transactions/{transaction_id}",
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )
    
    if response.status_code == 200:
        print(f"✓ Deleted transaction {transaction_id}")
    else:
        print(f"✗ Failed to delete transaction: {response.status_code} - {response.text}")

def test_performance_endpoint():
    """Test GET /performance"""
    print("\n=== Testing GET /performance ===")
    
    response = requests.get(f"{BASE_URL}/performance", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    
    if response.status_code == 200:
        performance = response.json()
        print(f"✓ Retrieved performance data:")
        print(f"  Transactions: {performance['num_transactions']}")
        print(f"  Tests: {performance['num_tests']}")
        print(f"  Linear search avg: {performance['linear_search']['average_time_seconds']:.8f}s")
        print(f"  Dictionary lookup avg: {performance['dictionary_lookup']['average_time_seconds']:.8f}s")
        print(f"  Dictionary is {performance['performance_improvement']['times_faster']:.2f}x faster")
    else:
        print(f"✗ Failed to get performance data: {response.status_code}")

def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    # Test 404 for non-existent transaction
    response = requests.get(f"{BASE_URL}/transactions/99999", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 404:
        print("✓ 404 error handled correctly for non-existent transaction")
    else:
        print(f"✗ Expected 404, got {response.status_code}")
    
    # Test 400 for invalid POST data
    invalid_data = {"type": "invalid"}  # Missing required fields
    response = requests.post(
        f"{BASE_URL}/transactions",
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        json=invalid_data,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 400:
        print("✓ 400 error handled correctly for invalid data")
    else:
        print(f"✗ Expected 400, got {response.status_code}")

def main():
    """Run all tests"""
    print("Transaction API Test Suite")
    print("=" * 50)
    
    # Test authentication first
    if not test_authentication():
        print("\n❌ Cannot proceed with tests - API server not accessible")
        return
    
    # Run all tests
    test_get_all_transactions()
    test_get_transaction_by_id()
    
    # Test CRUD operations
    created_id = test_create_transaction()
    if created_id:
        test_update_transaction(created_id)
        test_delete_transaction(created_id)
    
    test_performance_endpoint()
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")

if __name__ == "__main__":
    main()
