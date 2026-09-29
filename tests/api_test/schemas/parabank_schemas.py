"""ParaBank 接口响应契约模型（pydantic v2）。

字段结构来源：logs/contract_samples.txt
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    state: str
    zipCode: str


class Customer(BaseModel):
    id: int
    firstName: str
    lastName: str
    address: Address
    phoneNumber: str
    ssn: str


class Account(BaseModel):
    id: int
    customerId: int
    type: str
    balance: Decimal


class Transaction(BaseModel):
    id: int
    accountId: int
    type: str
    date: datetime
    amount: Decimal
    description: str


class LoanResponse(BaseModel):
    responseDate: datetime
    loanProviderName: str
    approved: bool
    accountId: Optional[int] = None


class BillPayResult(BaseModel):
    accountId: int
    amount: Decimal
    payeeName: str