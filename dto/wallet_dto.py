from pydantic import BaseModel
from enum import Enum
from decimal import Decimal

class Currency(Enum):
    BGN = "BGN"
    GBP = "GBP"
    USD = "USD"
    EUR = "EUR"

class WalletRequest(BaseModel):
    balance: str
    currency: Currency

class WalletResponse(BaseModel):
    balance: Decimal
    currency: str