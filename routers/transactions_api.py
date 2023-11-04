from fastapi import APIRouter, Depends, Header, Query, UploadFile
from typing import Annotated
from decimal import Decimal
import uuid
from repository.db_models import SessionLocal, Transaction
from sqlalchemy.orm import Session
from dto.transaction_dto import TransactionRequest, TransactionResponse, TransactionType

from repository.db_interaction import (add_transaction_locally, calculate_wallet_changes, get_all_user_transactions)
from service.image_processor import (process_nanonets_image, process_mindee_image, process_aws_image)
from service.authorization_logic import authorize_user

router = APIRouter()

# DB Configs:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("", response_model=TransactionResponse)
async def create_transaction(request: TransactionRequest,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):

    auth_user_id = authorize_user(authorization)["uid"]
    amount_decimal = Decimal(str(request.amount))
    transaction_type = request.type.name

    calculate_wallet_changes(auth_user_id, amount_decimal, transaction_type, db)

    transaction_model = Transaction(
        uid = str(uuid.uuid4()),
        category_id = request.category_id,
        description=request.description,
        amount=amount_decimal,
        type = transaction_type
    )

    add_transaction_locally(transaction_model, db)
    return transaction_model

@router.get("", response_model=list[TransactionResponse])
async def get_transactions(
    category_id: str = None,
    page: int = Query(1, ge=1),  # Default to page 1, minimum page is 1
    page_size: int = Query(10, le=100),  # Default page size is 10, max is 100
    db: Session = Depends(get_db),
    authorization: str = Header(None, alias="Authorization", description="Bearer Token")
):
    
    auth_user_id = authorize_user(authorization)["uid"]
    return get_all_user_transactions(page, page_size, auth_user_id, category_id, db)

        
@router.post("/extract")
async def process_image_aws(image: UploadFile,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):
    
    auth_user_id = authorize_user(authorization)["uid"]
    extracted_data = await process_aws_image(image)
    amount_decimal = Decimal(str(extracted_data["TOTAL"]))
    description = extracted_data["NAME"]
    transaction_type = TransactionType.EXPENSE.name

    calculate_wallet_changes(auth_user_id, amount_decimal, transaction_type, db)

    transaction_model = Transaction(
        uid = str(uuid.uuid4()),
        description=description,
        amount=amount_decimal,
        type = transaction_type
    )

    add_transaction_locally(transaction_model, db)
    return transaction_model

@router.post("/extract/mindee")
async def process_image_mindee(image: UploadFile):
    return await process_mindee_image(image)

@router.post("/extract/nanonet")
async def process_image_nanonet(image: UploadFile):
    return await process_nanonets_image(image)