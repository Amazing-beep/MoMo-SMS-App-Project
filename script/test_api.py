#!/usr/bin/env python3
"""
API Testing Script (Option-2 refactor, MoMo schema)
Requires: requests
Env overrides:
  BASE_URL (default http://localhost:8000)
  API_USER (default admin)
  API_PASS (default secret123)
"""

import os, base64, json, requests
from typing import Dict, Any, Optional

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
API_USER = os.getenv("API_USER", "admin")
API_PASS = os.getenv("API_PASS", "secret123")

def auth_header() -> Dict[str, str]:
    tok = base64.b64encode(f"{API_USER}:{API_PASS}".encode()).decode()
    return {"Authorization": f"Basic {tok}"}

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.auth = auth_header()

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def test_unauthorized(self):
        r = requests.get(self._url("/transactions"))
        print(f"GET /transactions (no auth) -> {r.status_code}")
        assert r.status_code == 401

    def test_get_all(self):
        r = requests.get(self._url("/transactions"), headers=self.auth)
        print(f"GET /transactions -> {r.status_code}")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body and "items" in body
        print(f" count={body['count']} items_shown={min(len(body['items']), 3)}")
        return body

    def test_create(self) -> int:
        payload = {
            "type": "CASHIN",
            "amount": 1000.0,
            "sender": "0788000001",
            "receiver": "0788000002",
            "timestamp": "2024-10-10T10:20:30Z"
        }
        r = requests.post(self._url("/transactions"), headers={**self.auth, "Content-Type":"application/json"}, json=payload)
        print(f"POST /transactions -> {r.status_code}")
        assert r.status_code == 201, r.text
        obj = r.json()
        assert "id" in obj
        print(f" created id={obj['id']}")
        return obj["id"]

    def test_get_one(self, tid: int):
        r = requests.get(self._url(f"/transactions/{tid}"), headers=self.auth)
        print(f"GET /transactions/{tid} -> {r.status_code}")
        assert r.status_code == 200
        obj = r.json()
        assert obj["id"] == tid

    def test_update(self, tid: int):
        payload = {"amount": 1500.5}
        r = requests.put(self._url(f"/transactions/{tid}"), headers={**self.auth, "Content-Type":"application/json"}, json=payload)
        print(f"PUT /transactions/{tid} -> {r.status_code}")
        assert r.status_code == 200
        obj = r.json()
        assert obj["amount"] == 1500.5

    def test_delete(self, tid: int):
        r = requests.delete(self._url(f"/transactions/{tid}"), headers=self.auth)
        print(f"DELETE /transactions/{tid} -> {r.status_code}")
        # Option-2 refactor returns 204 No Content
        assert r.status_code == 204
        assert not r.content

    def test_not_found(self):
        r = requests.get(self._url("/transactions/999999"), headers=self.auth)
        print(f"GET /transactions/999999 -> {r.status_code}")
        assert r.status_code == 404

    def run(self):
        print("== SMS API Test Suite ==")
        self.test_unauthorized()
        self.test_get_all()
        tid = self.test_create()
        self.test_get_one(tid)
        self.test_update(tid)
        self.test_delete(tid)
        self.test_not_found()
        print("All tests passed.")

if __name__ == "__main__":
    APITester().run()

