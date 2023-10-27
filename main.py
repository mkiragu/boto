from fastapi import FastAPI, Depends, HTTPException, UploadFile, Query
from pydantic import ValidationError
from uuid import uuid4
from enum import Enum
from fastapi import FastAPI, Header
from typing import Annotated
from repository.repository import SessionLocal, User, Category, Transaction, Wallet
from dto.user_dto import UserDTO
from dto.signup_request import SignupRequest
from dto.signin_request import SigninRequest
from dto.category_dto import CategoryRequest, CategoryResponse
from dto.wallet_dto import WalletRequest, WalletResponse, Currency
from dto.transaction_dto import TransactionRequest, TransactionResponse, TransactionType
from decimal import Decimal
from sqlalchemy.orm import Session
from service.image_processor import process_nanonets_image, process_mindee_image
from fastapi.middleware.cors import CORSMiddleware
import logging
import uuid

 # Firebase Configs:
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth
from requests.exceptions import HTTPError
cred = credentials.Certificate('mypfinance-service-account.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebase-config.json')))

# FastAPI Configs:
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

app = FastAPI()

allow_all = ['*']
app.add_middleware(
   CORSMiddleware,
   allow_origins=allow_all,
   allow_credentials=True,
   allow_methods=allow_all,
   allow_headers=allow_all
)

# DB Configs:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints 👇

@app.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    email = request.email
    password = request.password

    if not email or not password:
        raise HTTPException(detail='Error! Missing Email or Password', status_code=400)

    # Check if the user already exists in Firebase
    try:
        auth.get_user_by_email(email)
        raise HTTPException(detail='User with this email already exists', status_code=400)
    except auth.UserNotFoundError:
        # User doesn't exist, create a new user
        user = auth.create_user(email=email, password=password)
        logging.info('Successfully created user in Firebase!')

        user_model = User(
            uid=user.uid,
            username=request.username,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            age=request.age,
            gender=request.gender
        )

        add_user_locally(user_model, db)

        return JSONResponse(content={'message': 'Successfully created user'}, status_code=200)
    except Exception as error:
        logging.error(error)
        raise HTTPException(detail='Error Creating User', status_code=500)


@app.post("/signin")
async def signin(request: SigninRequest):
    try:
        user = pb.auth().sign_in_with_email_and_password(request.email, request.password)
        return JSONResponse(content={'token': user['idToken']}, status_code=200)
    except ValidationError as e:
        raise HTTPException(detail=str(e), status_code=400)
    except ValueError as e:
        raise HTTPException(detail=str(e), status_code=400)
    except HTTPError as e:
        raise HTTPException(detail='Failed to sign in. Please check your email and password.', status_code=400)
    
   
@app.get("/users", response_model=UserDTO)
async def get_user_info(db: Session = Depends(get_db),
                        authorization: Annotated[str | None, Header()] = None):
    
    user_id = authorize_user(authorization)["uid"]
    return get_user(user_id, db)

@app.post("/process-image/mindee")
async def process_image_mindee(image: UploadFile):
    return await process_mindee_image(image)

@app.post("/process-image/nanonet")
async def process_image_nanonet(image: UploadFile):
    return await process_nanonets_image(image)

@app.post("/wallet", response_model=WalletResponse)
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
        balance = balance_decimal,
        currency = request.currency
    )

    add_category_locally(wallet_model, db)
    return wallet_model

@app.post("/categories", response_model=CategoryResponse)
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

@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(request: TransactionRequest,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):

    auth_user_id = authorize_user(authorization)["uid"]
    amount_decimal = Decimal(str(request.amount))
    transaction_type = request.type

    # Calculate new wallet balance:
    user = get_user(auth_user_id, db)
    user_wallet = {}
    if user.wallets:
        user_wallet = user.wallets[0] 
    else:
        # User doesn't have a wallet, so create one
        user_wallet = Wallet(
            uid=str(uuid.uuid4()),
            user_id=auth_user_id,
            balance=amount_decimal,  # Initial balance is the transaction amount
            currenct = Currency.BGN # If none specified, we default to BGN
        )
        db.add(user_wallet)
        db.commit()

    if transaction_type == TransactionType.INCOME:
        user_wallet.balance += amount_decimal
    elif transaction_type == TransactionType.EXPENSE:
        user_wallet.balance -= amount_decimal
    
    db.commit()

    transaction_model = Transaction(
        uid = str(uuid.uuid4()),
        category_id = request.category_id,
        description=request.description,
        amount=amount_decimal,
        type = transaction_type.name
    )

    add_transaction_locally(transaction_model, db)
    return transaction_model

@app.get("/transactions")
async def get_transactions(
    category_id: str = None,
    page: int = Query(1, ge=1),  # Default to page 1, minimum page is 1
    page_size: int = Query(10, le=100),  # Default page size is 10, max is 100
    db: Session = Depends(get_db),
    authorization: str = Header(None, alias="Authorization", description="Bearer Token")
):
    
    auth_user_id = authorize_user(authorization)["uid"]

    offset = (page - 1) * page_size
    # Create a query to filter transactions based on user_id and optional category_id
    query = db.query(Transaction).join(Category).filter(Category.user_id == auth_user_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    # Apply pagination to the query
    transactions = query.offset(offset).limit(page_size).all()

    return transactions


def get_user(user_id: str, db: Session = Depends(get_db)):
    user = get_user_info(user_id, db)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

def get_user_info(user_id: str, db: Session = Depends(get_db)):
    return db.query(User).get(user_id)

def add_user_locally(user: User, db: Session = Depends(get_db)):
    # Create and add the new user to the database
    db.add(user)
    db.commit()
    db.refresh(user)

def add_wallet_locally(wallet: Wallet, db: Session = Depends(get_db)):
    # Create and add the new wallet to the database
    db.add(wallet)
    db.commit()
    db.refresh(wallet)

def add_category_locally(category: Category, db: Session = Depends(get_db)):
    # Create and add the new category to the database
    db.add(category)
    db.commit()
    db.refresh(category)

def add_transaction_locally(transaction: Transaction, db: Session = Depends(get_db)):
    # Create and add the new transaction to the database
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

def authorize_user(authorization: Annotated[str | None, Header()] = None):
    try:
        if authorization:
            decoded_token = auth.verify_id_token(authorization)
            # You can use the `decoded_token` for user authorization
            return decoded_token
        else:
            raise HTTPException(detail='Authorization token is missing', status_code=401)
    except auth.ExpiredIdTokenError:
        raise HTTPException(detail='JWT token has expired', status_code=401)
    except auth.InvalidIdTokenError:
        raise HTTPException(detail='Invalid JWT token', status_code=401)
    except Exception as e:
        raise HTTPException(detail=f'Authorization Error: {str(e)}', status_code=401)