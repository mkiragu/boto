from fastapi import APIRouter, Depends, Header
from typing import Annotated
from decimal import Decimal
import uuid
from repository.db_models import SessionLocal, User, Wallet
from sqlalchemy.orm import Session
from dto.wallet_dto import WalletRequest, WalletResponse

from repository.db_interaction import add_wallet_locally, get_wallet
from service.authorization_logic import authorize_user

router = APIRouter()

# DB Configs:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("", response_model=WalletResponse)
async def create_wallet(request: WalletRequest,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):

    auth_user_id = authorize_user(authorization)["uid"]
    db.query(User).get(auth_user_id)
    wallet_id = str(uuid.uuid4())
    balance_decimal = Decimal(str(request.balance))

    wallet_model = Wallet(
        uid = wallet_id,
        user_id = auth_user_id,
        name = request.name,
        balance = balance_decimal,
        currency = request.currency
    )

    add_wallet_locally(wallet_model, db)
    return wallet_model

@router.get("", response_model=WalletResponse)
async def get_wallet_info(db: Session = Depends(get_db),
                        authorization: Annotated[str | None, Header()] = None):
    
    user_id = authorize_user(authorization)["uid"]
    return get_wallet(user_id, db)