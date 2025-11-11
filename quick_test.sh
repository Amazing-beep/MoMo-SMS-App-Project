#!/bin/bash
echo "=================================================="
echo "Quick API Test"
echo "=================================================="
echo ""

# Check if server is running
echo "Checking if server is running on port 8000..."
if ! nc -z localhost 8000 2>/dev/null; then
    echo "❌ Server is not running on port 8000"
    echo ""
    echo "Please start the server first:"
    echo "  python api/api_server.py"
    echo ""
    exit 1
fi

echo "✓ Server is running"
echo ""

# Test 1: GET all transactions
echo "=================================================="
echo "Test 1: GET /transactions (with authentication)"
echo "=================================================="
curl -s -X GET http://localhost:8000/transactions \
  -u admin:password123 \
  -H "Content-Type: application/json" | head -30

echo ""
echo ""

# Test 2: GET without auth (should fail)
echo "=================================================="
echo "Test 2: GET /transactions (NO authentication)"
echo "=================================================="
curl -s -X GET http://localhost:8000/transactions

echo ""
echo ""

# Test 3: GET specific transaction
echo "=================================================="
echo "Test 3: GET /transactions/1"
echo "=================================================="
curl -s -X GET http://localhost:8000/transactions/1 \
  -u admin:password123

echo ""
echo ""

# Test 4: POST new transaction
echo "=================================================="
echo "Test 4: POST /transactions (create new)"
echo "=================================================="
curl -s -X POST http://localhost:8000/transactions \
  -u admin:password123 \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "amount": 150.00,
    "sender": "+1234567890",
    "receiver": "+9876543210",
    "description": "Test transaction from script"
  }'

echo ""
echo ""

echo "=================================================="
echo "All tests completed!"
echo "=================================================="