from fastapi import FastAPI, Depends, HTTPException, UploadFile
from uuid import uuid4
from fastapi import FastAPI, Header
from typing import Annotated
from repository.repository import SessionLocal, User, Category, Transaction
from dto.user_dto import UserDTO
from dto.signup_request import SignupRequest
from dto.signin_request import SigninRequest
from dto.category_request import CategoryRequest
from dto.transaction_request import TransactionRequest
from decimal import Decimal
from sqlalchemy.orm import Session
from service.image_processor import process_nanonets_image, process_mindee_image
from fastapi.middleware.cors import CORSMiddleware
import logging
import uuid

 # Firebase SignIn/SignUp imports
import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth
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

cred = credentials.Certificate('mypfinance-service-account.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebase-config.json')))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# TODO Error handling of when user with email already exists; 
# What would happen when the DB fails but Firebase is successful?
@app.post("/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
   email = request.email
   password = request.password

   if email is None or password is None:
       return HTTPException(detail={'message': 'Error! Missing Email or Password'}, status_code=400)
   try:
       user = auth.create_user(
           email=email,
           password=password
       )
       
       logging.info('Successfully created user in Firebase!')

       user_model = User(
            uid=user.uid,
            username=request.username,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            age=request.age,
            gender = request.gender
        )
       
       add_user_locally(user_model, db)

       return JSONResponse(content={'message': f'Successfully created user'}, status_code=200)    
   except Exception as error:
       logging.error(error)
       return HTTPException(detail={'message': 'Error Creating User'}, status_code=400)

@app.post("/signin")
async def signin(request: SigninRequest):
   try:
       user = pb.auth().sign_in_with_email_and_password(request.email, request.password)
       return JSONResponse(content={'token': user['idToken']}, status_code=200)
   except:
       return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)
   
@app.get("/users/{user_id}", response_model=UserDTO)
async def get_user_info(user_id: str, 
                        db: Session = Depends(get_db),
                        authorization: Annotated[str | None, Header()] = None):
    
    auth_id = authorize_user(authorization)["uid"]
    user = get_user_info(auth_id, user_id, db)

    logging.info(user.categories)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/process-image/mindee")
async def process_image_mindee(image: UploadFile):
    return await process_mindee_image(image)

@app.post("/process-image/nanonet")
async def process_image_nanonet(image: UploadFile):
    return await process_nanonets_image(image)

@app.post("/category")
async def create_category(request: CategoryRequest,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):

    user = authorize_user(authorization)
    db.query(User).get(user["uid"])

    category_model = Category(
        uid = str(uuid.uuid4()),
        user_id = user["uid"],
        name = request.name
    )

    add_category_locally(category_model, db)
    return JSONResponse(content={'message': f'Successfully created category'}, status_code=200)    

@app.post("/transaction")
async def create_transaction(request: TransactionRequest,
                    db: Session = Depends(get_db),
                    authorization: Annotated[str | None, Header()] = None):

    authorize_user(authorization)

    amount_decimal = Decimal(str(request.amount))

    transaction_model = Transaction(
        uid = str(uuid.uuid4()),
        category_id = request.category_id,
        description=request.description,
        amount=amount_decimal
    )

    add_transaction_locally(transaction_model, db)
    return JSONResponse(content={'message': f'Successfully created transaction'}, status_code=200)    

def get_user_info(auth_id: str, user_id: str, db: Session = Depends(get_db)):
    return db.query(User).filter(auth_id == user_id).first()

def add_user_locally(user: User, db: Session = Depends(get_db)):
    # Create and add the new user to the database
    db.add(user)
    db.commit()
    db.refresh(user)

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


# TODO What about failed authorization attemp? What about wrong JWT?
def authorize_user(authorization: Annotated[str | None, Header()] = None):
    return auth.verify_id_token(authorization)