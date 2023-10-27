from pydantic import BaseModel

class TransactionRequest(BaseModel):
    category_id: str
    description: str
    amount: float