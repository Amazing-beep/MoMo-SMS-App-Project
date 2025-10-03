#!/usr/bin/env bash
set -euo pipefail

# SMS API Curl Test Script (MoMo schema)
# Works with Option-2 server refactor that uses:
#  - Basic Auth (admin/secret123 by default via env)
#  - GET /transactions -> {count, items:[...]}
#  - 204 No Content on DELETE

BASE_URL="${BASE_URL:-http://localhost:8000}"
API_USER="${API_USER:-admin}"
API_PASS="${API_PASS:-secret123}"
AUTH_HEADER="Authorization: Basic $(printf "%s" "$API_USER:$API_PASS" | base64)"

have_jq() { command -v jq >/dev/null 2>&1; }

pp() {
  if have_jq; then jq '.' || true; else cat; fi
}

echo "SMS API Curl Tests"
echo "=================="
echo "Base: $BASE_URL"
echo

echo "1) Unauthorized GET /transactions (expect 401)"
curl -i -sS "$BASE_URL/transactions" | sed -n '1,15p'
echo

echo "2) Authorized GET /transactions (expect 200 + count/items)"
curl -sS -H "$AUTH_HEADER" "$BASE_URL/transactions" | pp
echo

echo "3) POST /transactions (create, expect 201)"
CREATE_PAY='{
  "type":"CASHIN",
  "amount":5000.0,
  "sender":"0788000001",
  "receiver":"0788000002",
  "timestamp":"2024-10-10T10:20:30Z"
}'
created=$(curl -sS -X POST -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d "$CREATE_PAY" "$BASE_URL/transactions")
echo "$created" | pp
new_id=$(echo "$created" | (jq -r '.id' 2>/dev/null || true))
echo "   new_id=$new_id"
echo

echo "4) GET /transactions/$new_id (expect 200)"
curl -sS -H "$AUTH_HEADER" "$BASE_URL/transactions/$new_id" | pp
echo

echo "5) PUT /transactions/$new_id (update amount, expect 200)"
UPDATE_PAY='{"amount":6500.0}'
curl -sS -X PUT -H "$AUTH_HEADER" -H "Content-Type: application/json" \
  -d "$UPDATE_PAY" "$BASE_URL/transactions/$new_id" | pp
echo

echo "6) DELETE /transactions/$new_id (expect 204, no body)"
curl -i -sS -X DELETE -H "$AUTH_HEADER" "$BASE_URL/transactions/$new_id" | sed -n '1,8p'
echo

echo "7) GET missing /transactions/999999 (expect 404)"
curl -i -sS -H "$AUTH_HEADER" "$BASE_URL/transactions/999999" | sed -n '1,15p'
echo

echo "Done."

