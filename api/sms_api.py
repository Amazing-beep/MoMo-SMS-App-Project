#!/usr/bin/env python3
# api/server.py
import os, json, base64, re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from dsa.parse_and_search import (
    load_transactions, save_transactions,
    get_transaction_by_id, add_transaction,
    update_transaction, delete_transaction
)

# --- Config (env-based) ---
USERS = { os.getenv("API_USER", "admin"): os.getenv("API_PASS", "secret123") }
REALM = "MoMoAPI"
DATA_FILE = os.getenv("DATA_FILE", "modified_sms_v2.xml")
STORE_FILE = os.getenv("STORE_FILE", "transactions_store.json")
PORT = int(os.getenv("PORT", "8000"))

# --- State (shared list+dict+next_id) ---
STATE = load_transactions(DATA_FILE, STORE_FILE)

def _ok_auth(header_value: str) -> bool:
    if not header_value or not header_value.startswith("Basic "): return False
    try:
        decoded = base64.b64decode(header_value.split(" ", 1)[1]).decode("utf-8")
        user, pw = decoded.split(":", 1)
        return USERS.get(user) == pw
    except Exception:
        return False

def _unauth(h: BaseHTTPRequestHandler):
    h.send_response(401)
    h.send_header("WWW-Authenticate", f'Basic realm="{REALM}"')
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Content-Type", "application/json")
    h.end_headers()
    h.wfile.write(json.dumps({"error":"Unauthorized","message":"Invalid credentials"}).encode())

def _send_json(h: BaseHTTPRequestHandler, code: int, payload):
    data = json.dumps(payload).encode("utf-8")
    h.send_response(code)
    h.send_header("Content-Type", "application/json")
    h.send_header("Content-Length", str(len(data)))
    h.send_header("Access-Control-Allow-Origin", "*")
    h.end_headers()
    h.wfile.write(data)

def _parse_id(path: str):
    m = re.match(r"^/transactions/(\d+)$", path)
    return int(m.group(1)) if m else None

class Handler(BaseHTTPRequestHandler):
    # Quiet default logging (optional)
    def log_message(self, format, *args): return

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization,Content-Type")
        self.end_headers()

    def _require_auth(self):
        if not _ok_auth(self.headers.get("Authorization")):
            _unauth(self)
            return False
        return True

    def _json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b""
            return json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            _send_json(self, 400, {"error":"BadRequest","message":"Invalid JSON"})
            return None

    def do_GET(self):
        if not self._require_auth(): return
        parsed = urlparse(self.path)
        if parsed.path == "/transactions":
            _send_json(self, 200, {"count": len(STATE["list"]), "items": STATE["list"]})
            return
        tid = _parse_id(parsed.path)
        if tid is not None:
            tx = get_transaction_by_id(STATE, tid)
            if not tx:
                _send_json(self, 404, {"error":"NotFound","message":"Transaction not found"})
            else:
                _send_json(self, 200, tx)
            return
        _send_json(self, 404, {"error":"NotFound","message":"Endpoint not found"})

    def do_POST(self):
        if not self._require_auth(): return
        if self.path != "/transactions":
            _send_json(self, 404, {"error":"NotFound","message":"Endpoint not found"}); return
        payload = self._json_body()
        if payload is None: return
        # Server assigns id; validation happens in add_transaction (may raise ValueError)
        try:
            tx = add_transaction(STATE, payload)
        except ValueError as e:
            _send_json(self, 400, {"error":"BadRequest","message":str(e)}); return
        save_transactions(STATE, STORE_FILE)
        _send_json(self, 201, tx)

    def do_PUT(self):
        if not self._require_auth(): return
        tid = _parse_id(self.path)
        if tid is None:
            _send_json(self, 404, {"error":"NotFound","message":"Endpoint not found"}); return
        payload = self._json_body()
        if payload is None: return
        try:
            tx = update_transaction(STATE, tid, payload)
        except ValueError as e:
            _send_json(self, 400, {"error":"BadRequest","message":str(e)}); return
        if not tx:
            _send_json(self, 404, {"error":"NotFound","message":"Transaction not found"}); return
        save_transactions(STATE, STORE_FILE)
        _send_json(self, 200, tx)

    def do_DELETE(self):
        if not self._require_auth(): return
        tid = _parse_id(self.path)
        if tid is None:
            _send_json(self, 404, {"error":"NotFound","message":"Endpoint not found"}); return
        ok = delete_transaction(STATE, tid)
        if not ok:
            _send_json(self, 404, {"error":"NotFound","message":"Transaction not found"}); return
        save_transactions(STATE, STORE_FILE)
        # Proper 204: no body, still include CORS
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    # Nice-to-have: explicit 405s if someone hits unsupported verbs
    def do_HEAD(self): self._method_not_allowed()
    def do_PATCH(self): self._method_not_allowed()
    def _method_not_allowed(self):
        _send_json(self, 405, {"error":"MethodNotAllowed","message":"Use GET/POST/PUT/DELETE"})

def run():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"✅ Server running on http://0.0.0.0:{PORT}")
    print("   Basic Auth user:", list(USERS.keys())[0])
    server.serve_forever()

if __name__ == "__main__":
    run()

