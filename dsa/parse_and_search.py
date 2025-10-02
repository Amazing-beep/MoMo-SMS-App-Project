import os, json, time
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET

def _make_state(items: List[Dict[str, Any]]):
    index = { int(it['id']): it for it in items }
    next_id = (max(index.keys()) + 1) if index else 1
    return {'list': items, 'index': index, 'next_id': next_id}

def parse_xml_to_list(xml_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(xml_path):
        return [
            {"id": 1, "type": "CASHIN", "amount": 5000, "sender": "0788000001", "receiver": "0788000002", "timestamp": "2024-10-10T10:20:30Z"}
        ]
    tree = ET.parse(xml_path)
    root = tree.getroot()
    items, next_id = [], 1
    for tx in root.findall(".//transaction"):
        obj = {
            "id": int(tx.get("id") or next_id),
            "type": (tx.findtext("type") or "").upper(),
            "amount": float(tx.findtext("amount") or 0),
            "sender": tx.findtext("sender") or "",
            "receiver": tx.findtext("receiver") or "",
            "timestamp": tx.findtext("timestamp") or ""
        }
        items.append(obj)
        next_id = obj["id"] + 1
    return items

def load_transactions(xml_path: str, store_path: str):
    if os.path.exists(store_path):
        with open(store_path, "r", encoding="utf-8") as f:
            return _make_state(json.load(f))
    items = parse_xml_to_list(xml_path)
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
    return _make_state(items)

def save_transactions(state, store_path: str):
    with open(store_path, "w", encoding="utf-8") as f:
        json.dump(state['list'], f, indent=2)

def get_transaction_by_id(state, tid: int): return state['index'].get(tid)

def add_transaction(state, payload: Dict[str, Any]):
    tid = int(payload.get("id") or state['next_id'])
    obj = {
        "id": tid,
        "type": str(payload.get("type", "")).upper(),
        "amount": float(payload.get("amount", 0)),
        "sender": payload.get("sender", ""),
        "receiver": payload.get("receiver", ""),
        "timestamp": payload.get("timestamp", "")
    }
    state['list'].append(obj)
    state['index'][tid] = obj
    state['next_id'] = tid + 1
    return obj

def update_transaction(state, tid: int, payload: Dict[str, Any]):
    tx = state['index'].get(tid)
    if not tx: return None
    for k in ("type","amount","sender","receiver","timestamp"):
        if k in payload:
            tx[k] = float(payload[k]) if k=="amount" else payload[k]
    return tx

def delete_transaction(state, tid: int):
    if tid not in state['index']: return False
    state['list'] = [t for t in state['list'] if int(t['id']) != tid]
    state['index'].pop(tid)
    return True

def linear_search(items: List[Dict[str, Any]], tid: int):
    for it in items:
        if int(it["id"]) == tid:
            return it
    return None

def dict_lookup(index: Dict[int, Dict[str, Any]], tid: int):
    return index.get(tid)

def benchmark_search(state, trials: int = 1000):
    import random
    items, index = state['list'], state['index']
    ids = [int(it["id"]) for it in items]
    candidates = ids + [max(ids)+k for k in range(1, 6)]
    t0 = time.perf_counter()
    for _ in range(trials):
        linear_search(items, random.choice(candidates))
    t1 = time.perf_counter()
    t2 = time.perf_counter()
    for _ in range(trials):
        dict_lookup(index, random.choice(candidates))
    t3 = time.perf_counter()
    return {
        "linear_ms": round((t1 - t0) * 1000, 3),
        "dict_ms": round((t3 - t2) * 1000, 3)
    }

if __name__ == "__main__":
    state = load_transactions("modified_sms_v2.xml", "transactions_store.json")
    print(json.dumps(benchmark_search(state), indent=2))

