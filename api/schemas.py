from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    sms_address: str
    sms_date: datetime
    sms_type: str
    sms_body: str
    transaction_type: str
    amount: int
    currency: str = Field(default="RWF")
    sender: Optional[str] = None
    receiver: Optional[str] = None
    balance: Optional[int] = None
    fee: int = 0
    transaction_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    message: str
    readable_date: Optional[str] = None
    contact_name: Optional[str] = None
    raw_json: Any


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    sms_address: Optional[str] = None
    sms_date: Optional[datetime] = None
    sms_type: Optional[str] = None
    sms_body: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    balance: Optional[int] = None
    fee: Optional[int] = None
    transaction_id: Optional[str] = None
    external_transaction_id: Optional[str] = None
    message: Optional[str] = None
    readable_date: Optional[str] = None
    contact_name: Optional[str] = None
    raw_json: Optional[Any] = None


class Transaction(TransactionBase):
    id: int


__all__ = [
    "TransactionBase",
    "TransactionCreate",
    "TransactionUpdate",
    "Transaction",
]