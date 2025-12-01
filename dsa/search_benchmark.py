from __future__ import annotations

import os
import sys
import random
import statistics
import time
from typing import Dict, List, Optional, Tuple, Any


# Ensure project root on sys.path to import api.db
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from api.db import get_connection
except Exception:  # pragma: no cover
    from db import get_connection


def load_transactions_from_db(limit: int = 100) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM transactions ORDER BY id ASC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def linear_search(
    transactions: List[Dict[str, Any]], target_id: int
) -> Optional[Dict[str, Any]]:
    for item in transactions:
        if item.get("id") == target_id:
            return item
    return None


def dict_lookup(
    index: Dict[int, Dict[str, Any]], target_id: int
) -> Optional[Dict[str, Any]]:
    return index.get(target_id)


def build_index(transactions: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    return {int(t["id"]): t for t in transactions}


def benchmark(num_targets: int = 20, repetitions: int = 1000) -> None:
    transactions = load_transactions_from_db(limit=max(num_targets, 100))
    if len(transactions) < 20:
        raise RuntimeError(
            "Need at least 20 transactions in the database to benchmark."
        )

    candidate_ids = [int(t["id"]) for t in transactions]
    targets = random.sample(candidate_ids, k=num_targets)

    index = build_index(transactions)

    linear_times: List[float] = []
    dict_times: List[float] = []

    # Warmup
    for tid in targets:
        _ = linear_search(transactions, tid)
        _ = dict_lookup(index, tid)

    # Timed runs
    for tid in targets:
        start = time.perf_counter()
        for _ in range(repetitions):
            _ = linear_search(transactions, tid)
        linear_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        for _ in range(repetitions):
            _ = dict_lookup(index, tid)
        dict_times.append(time.perf_counter() - start)

    linear_avg = statistics.mean(linear_times)
    dict_avg = statistics.mean(dict_times)

    print("=== Search Benchmark (by id) ===")
    print(f"Records searched: {len(transactions)}")
    print(f"Targets: {num_targets}, Repetitions per target: {repetitions}")
    print(f"Linear search avg time: {linear_avg:.6f}s")
    print(f"Dict lookup avg time:  {dict_avg:.6f}s")
    speedup = linear_avg / dict_avg if dict_avg > 0 else float("inf")
    print(f"Estimated speedup (linear/dict): {speedup:.1f}x")


if __name__ == "__main__":
    benchmark()