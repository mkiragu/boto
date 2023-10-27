from pydantic import BaseModel
from enum import Enum

class TransactionType(Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class TransactionRequest(BaseModel):
    category_id: str
    description: str
    amount: float
    type: TransactionType

class TransactionResponse(BaseModel):
    uid: str