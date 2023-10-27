from pydantic import BaseModel
from enum import Enum

class Currency(Enum):
    BGN = "BGN"
    GBP = "GBP"
    USD = "USD"
    EUR = "EUR"

class WalletRequest(BaseModel):
    balance: str
    currency: Currency

class WalletResponse(BaseModel):
    uid: str
    balance: str
    currency: str