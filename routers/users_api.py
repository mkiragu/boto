from fastapi import APIRouter, Depends, Header
from typing import Annotated
from repository.db_models import SessionLocal
from sqlalchemy.orm import Session
from dto.user_dto import UserDTO

from service.authorization_logic import authorize_user
from repository.db_interaction import get_user

router = APIRouter()

# DB Configs:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("", response_model=UserDTO)
async def get_user_info(db: Session = Depends(get_db),
                        authorization: Annotated[str | None, Header()] = None):
    
    user_id = authorize_user(authorization)["uid"]
    return get_user(user_id, db)