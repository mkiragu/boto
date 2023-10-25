from fastapi import FastAPI, Depends, HTTPException, UploadFile
from uuid import uuid4
from fastapi import FastAPI, Header
from typing import Annotated
from repository.users_repository import SessionLocal, User
from dto.user_dto import UserDTO
from dto.signup_request import SignupRequest
from dto.signin_request import SigninRequest
from sqlalchemy.orm import Session
from service.image_processor import process_nanonets_image, process_mindee_image
from fastapi.middleware.cors import CORSMiddleware
import logging

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
            id=user.uid,
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
       jwt = user['idToken']
       return JSONResponse(content={'token': jwt}, status_code=200)
   except:
       return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)
   
@app.get("/users/{user_id}", response_model=UserDTO)
async def get_user_info(user_id: str, 
                        db: Session = Depends(get_db),
                        authorization: Annotated[str | None, Header()] = None):
    
    auth_user = authorize_user(authorization)
    user = db.query(User).filter(auth_user["uid"] == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/process-image/mindee")
async def process_image_mindee(image: UploadFile):
    return await process_mindee_image(image)

@app.post("/process-image/nanonet")
async def process_image_nanonet(image: UploadFile):
    return await process_nanonets_image(image)

def add_user_locally(user: User, db: Session = Depends(get_db)):
    # Create and add the new user to the database
    db.add(user)
    db.commit()
    db.refresh(user)

def authorize_user(authorization: Annotated[str | None, Header()] = None):
    return auth.verify_id_token(authorization)