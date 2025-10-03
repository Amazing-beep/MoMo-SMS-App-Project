#!/usr/bin/env python3
"""
Project setup for MoMo SMS REST API
- Ensures XML exists
- Initializes JSON store via dsa.parse_and_search
- Runs DSA benchmark
- Prints next steps for running the server and tests
"""

import os
import sys
import json
import importlib

ROOT = os.path.dirname(os.path.abspath(__file__))

def ensure_xml():
    xml_path = os.path.join(ROOT, "modified_sms_v2.xml")
    if not os.path.exists(xml_path):
        print("✗ Error: modified_sms_v2.xml not found at project root.")
        return None
    print("✓ Found modified_sms_v2.xml")
    return xml_path

def init_store():
    sys.path.insert(0, ROOT)
    pns = importlib.import_module("dsa.parse_and_search")
    data_file = os.getenv("DATA_FILE", "modified_sms_v2.xml")
    store_file = os.getenv("STORE_FILE", "transactions_store.json")
    state = pns.load_transactions(data_file, store_file)
    print(f"✓ Initialized store -> {store_file} ({len(state['list'])} records)")
    return pns, state, store_file

def run_benchmark(pns, state):
    results = pns.benchmark_search(state, trials=1000)
    print("✓ DSA benchmark (hits+misses):")
    print(json.dumps(results, indent=2))

def next_steps():
    print("\n=== Next steps ===")
    print("1) Run server:")
    print("   export API_USER=admin API_PASS=secret123 PORT=8000")
    print("   python -m api.server")
    print("\n2) Test with curl:")
    print("   bash curl_tests.sh")
    print("\n3) Or run your Python tests (requests):")
    print("   python test_api.py")

def main():
    print("MoMo SMS REST API - Setup")
    print("=========================")
    if not ensure_xml():
        sys.exit(1)
    pns, state, store = init_store()
    run_benchmark(pns, state)
    next_steps()

if __name__ == "__main__":
    main()

