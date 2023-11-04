from fastapi import APIRouter, Depends, Header, Query
from typing import Annotated
import uuid
from repository.db_models import SessionLocal, User, Category
from sqlalchemy.orm import Session
from dto.category_dto import CategoryRequest, CategoryResponse

from repository.db_interaction import (add_category_locally, get_all_user_categories)
from service.authorization_logic import authorize_user

router = APIRouter()

# DB Configs:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=CategoryResponse)
async def create_category(request: CategoryRequest,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):

    auth_user_id = authorize_user(authorization)["uid"]
    db.query(User).get(auth_user_id)
    category_id = str(uuid.uuid4())

    category_model = Category(
        uid = category_id,
        user_id = auth_user_id,
        name = request.name.upper()
    )

    add_category_locally(category_model, db)
    return category_model

@router.get("", response_model=list[CategoryResponse])
async def get_categories(
    page: int = Query(1, ge=1),  # Default to page 1, minimum page is 1
    page_size: int = Query(10, le=100),  # Default page size is 10, max is 100
    db: Session = Depends(get_db),
    authorization: str = Header(None, alias="Authorization", description="Bearer Token")
):
    
    auth_user_id = authorize_user(authorization)["uid"]
    return get_all_user_categories(page, page_size, auth_user_id, db)