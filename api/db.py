import os
import sys
import sqlite3
from contextlib import closing
from typing import Iterable, List

# Ensure project root is on sys.path so we can import the 'dsa' package
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dsa.data_loader import load_data_from_xml
from api.schemas import TransactionCreate


DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "db.sqlite3")
RAW_XML_PATH = os.path.join(DATA_DIR, "raw", "momo.xml")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_table() -> None:
    with closing(get_connection()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sms_address TEXT NOT NULL,
                sms_date TEXT NOT NULL,
                sms_type TEXT NOT NULL,
                sms_body TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL,
                sender TEXT,
                receiver TEXT,
                balance INTEGER,
                fee INTEGER NOT NULL DEFAULT 0,
                transaction_id TEXT,
                external_transaction_id TEXT,
                message TEXT NOT NULL,
                readable_date TEXT,
                contact_name TEXT,
                raw_json TEXT NOT NULL
            )
            """
        )


def _insert_transactions(transactions: Iterable[TransactionCreate]) -> None:
    with closing(get_connection()) as conn, conn:
        conn.executemany(
            """
            INSERT INTO transactions (
                sms_address, sms_date, sms_type, sms_body, transaction_type, amount, currency,
                sender, receiver, balance, fee, transaction_id, external_transaction_id, message,
                readable_date, contact_name, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    t.sms_address,
                    t.sms_date.isoformat(),
                    t.sms_type,
                    t.sms_body,
                    t.transaction_type,
                    t.amount,
                    t.currency,
                    t.sender,
                    t.receiver,
                    t.balance,
                    t.fee,
                    t.transaction_id,
                    t.external_transaction_id,
                    t.message,
                    t.readable_date,
                    t.contact_name,
                    __import__("json").dumps(t.raw_json),
                )
                for t in transactions
            ],
        )


def initialize_database() -> None:
    # Remove existing database file if present
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    # Ensure parent directory exists
    parent_dir = os.path.dirname(DATABASE_PATH)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    # Create tables
    ensure_table()

    # Load and populate transactions from raw XML, transformed to our schema
    raw_items = load_data_from_xml(RAW_XML_PATH)

    # # Log raw_items to a file for inspection
    # import json as _json

    # with open("raw_items_log.json", "w", encoding="utf-8") as f:
    #     _json.dump(raw_items, f, ensure_ascii=False, indent=2)

    if not raw_items:
        return

    transformed: List[TransactionCreate] = []
    from datetime import datetime, timezone
    import math

    for item in raw_items:
        timestamp_ms = item.get("timestamp_ms") or 0
        dt = datetime.fromtimestamp((timestamp_ms or 0) / 1000.0, tz=timezone.utc)
        amount_float = item.get("amount") or 0.0
        amount_int = int(math.floor(amount_float))

        tx = TransactionCreate(
            sms_address=item.get("sms_address") or "N/A",
            sms_date=dt,
            sms_type="SMS",
            sms_body=item.get("raw_body") or "",
            transaction_type=item.get("type") or "unknown",
            amount=amount_int,
            currency="RWF",
            sender=None,
            receiver=None,
            balance=None,
            fee=int(math.floor((item.get("fee") or 0.0)) or 0),
            transaction_id=(item.get("tx_id") or None),
            external_transaction_id=None,
            message=item.get("raw_body") or "",
            readable_date=item.get("readable_date") or None,
            contact_name=None,
            raw_json=item,
        )
        transformed.append(tx)

    _insert_transactions(transformed)