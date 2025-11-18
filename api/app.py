from __future__ import annotations

import base64
from contextlib import closing
from typing import List, Optional, Any, Dict
import json

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

try:
    # When running via `uvicorn api.app:app` (package import)
    from api.db import get_connection, ensure_table, initialize_database
except Exception:
    # When running file directly: `python api/app.py`
    from db import get_connection, ensure_table, initialize_database


# -----------------------------
# Basic Authorization (Base64)
# -----------------------------
def parse_basic_auth_header(request: Request) -> tuple[str, str]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Basic Authorization header",
        )

    try:
        encoded_credentials = auth_header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        if ":" not in decoded:
            raise ValueError("Invalid basic auth format")
        username, password = decoded.split(":", 1)
        return username, password
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Basic Authorization header",
        )


def require_basic_auth(
    credentials: tuple[str, str] = Depends(parse_basic_auth_header),
) -> None:
    username, password = credentials
    expected_username = "admin"
    expected_password = "secret"
    if not (username == expected_username and password == expected_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )


# -----------------------------
# Pydantic Schemas (import from api.schemas with fallback)
# -----------------------------
try:
    from api.schemas import Transaction, TransactionCreate, TransactionUpdate
except Exception:
    from schemas import Transaction, TransactionCreate, TransactionUpdate


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="SMS Transactions API")


@app.on_event("startup")
def on_startup() -> None:
    # Recreate and repopulate the database on each server start
    initialize_database()


# -----------------------------
# CRUD Endpoints
# -----------------------------
@app.get(
    "/transactions",
    response_model=List[Transaction],
    dependencies=[Depends(require_basic_auth)],
)
def list_transactions() -> List[Transaction]:
    with closing(get_connection()) as conn:
        rows = conn.execute("SELECT * FROM transactions ORDER BY id ASC").fetchall()
        items: List[Dict[str, Any]] = []
        for row in rows:
            data = dict(row)
            if data.get("raw_json"):
                try:
                    data["raw_json"] = json.loads(data["raw_json"])  # type: ignore
                except Exception:
                    data["raw_json"] = None
            items.append(data)
        return [Transaction(**item) for item in items]


@app.get(
    "/transactions/{transaction_id}",
    response_model=Transaction,
    dependencies=[Depends(require_basic_auth)],
)
def get_transaction(transaction_id: int) -> Transaction:
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
        data = dict(row)
        if data.get("raw_json"):
            try:
                data["raw_json"] = json.loads(data["raw_json"])  # type: ignore
            except Exception:
                data["raw_json"] = None
        return Transaction(**data)


@app.post(
    "/transactions",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_basic_auth)],
)
def create_transaction(payload: TransactionCreate) -> Transaction:
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute(
            """
            INSERT INTO transactions (
                sms_address, sms_date, sms_type, sms_body, transaction_type, amount, currency,
                sender, receiver, balance, fee, transaction_id, external_transaction_id, message,
                readable_date, contact_name, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.sms_address,
                payload.sms_date.isoformat(),
                payload.sms_type,
                payload.sms_body,
                payload.transaction_type,
                payload.amount,
                payload.currency,
                payload.sender,
                payload.receiver,
                payload.balance,
                payload.fee,
                payload.transaction_id,
                payload.external_transaction_id,
                payload.message,
                payload.readable_date,
                payload.contact_name,
                (
                    json.dumps(payload.raw_json)
                    if payload.raw_json is not None
                    else json.dumps({})
                ),
            ),
        )
        new_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (new_id,)
        ).fetchone()
        data = dict(row)
        if data.get("raw_json"):
            try:
                data["raw_json"] = json.loads(data["raw_json"])  # type: ignore
            except Exception:
                data["raw_json"] = None
        return Transaction(**data)


@app.put(
    "/transactions/{transaction_id}",
    response_model=Transaction,
    dependencies=[Depends(require_basic_auth)],
)
def update_transaction(transaction_id: int, payload: TransactionUpdate) -> Transaction:
    with closing(get_connection()) as conn, conn:
        existing = conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )

        # Build dynamic update based on provided fields
        fields = [
            ("sms_address", payload.sms_address),
            ("sms_date", payload.sms_date.isoformat() if payload.sms_date else None),
            ("sms_type", payload.sms_type),
            ("sms_body", payload.sms_body),
            ("transaction_type", payload.transaction_type),
            ("amount", payload.amount),
            ("currency", payload.currency),
            ("sender", payload.sender),
            ("receiver", payload.receiver),
            ("balance", payload.balance),
            ("fee", payload.fee),
            ("transaction_id", payload.transaction_id),
            ("external_transaction_id", payload.external_transaction_id),
            ("message", payload.message),
            ("readable_date", payload.readable_date),
            ("contact_name", payload.contact_name),
            (
                "raw_json",
                json.dumps(payload.raw_json) if payload.raw_json is not None else None,
            ),
        ]
        set_clauses = []
        values: List[object] = []
        for column, value in fields:
            if value is not None:
                set_clauses.append(f"{column} = ?")
                values.append(value)

        if not set_clauses:
            row = conn.execute(
                "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
            ).fetchone()
            data = dict(row)
            if data.get("raw_json"):
                try:
                    data["raw_json"] = json.loads(data["raw_json"])  # type: ignore
                except Exception:
                    data["raw_json"] = None
            return Transaction(**data)

        values.append(transaction_id)
        sql = f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id = ?"
        conn.execute(sql, tuple(values))
        row = conn.execute(
            "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        data = dict(row)
        if data.get("raw_json"):
            try:
                data["raw_json"] = json.loads(data["raw_json"])  # type: ignore
            except Exception:
                data["raw_json"] = None
        return Transaction(**data)


@app.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_basic_auth)],
)
def delete_transaction(transaction_id: int) -> JSONResponse:
    with closing(get_connection()) as conn, conn:
        row = conn.execute(
            "SELECT id FROM transactions WHERE id = ?", (transaction_id,)
        ).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
        conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)


# -----------------------------
# Uvicorn Entrypoint
# -----------------------------
def run() -> None:
    import uvicorn

    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
