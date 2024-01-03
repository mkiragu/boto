from fastapi import APIRouter, Depends
from repository.db_models import SessionLocal, User
from repository.db_interaction import setup_user
from dto.signup_request import SignupRequest
from dto.signin_request import SigninRequest
from pydantic import ValidationError
from sqlalchemy.orm import Session
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
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

router = APIRouter()

# DB Configs:
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", )
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

        setup_user(user_model, db)

        return JSONResponse(content={'message': 'Successfully created user'}, status_code=200, media_type='application/json')
    except Exception as error:
        logging.error(error)
        raise HTTPException(detail='Error Creating User', status_code=500)


@router.post("/signin")
async def signin(request: SigninRequest):
    try:
        user = pb.auth().sign_in_with_email_and_password(request.email, request.password)
        return JSONResponse(content={'token': user['idToken']}, status_code=200, media_type='application/json')
    except ValidationError as e:
        raise HTTPException(detail=str(e), status_code=400)
    except ValueError as e:
        raise HTTPException(detail=str(e), status_code=400)
    except HTTPError as e:
        raise HTTPException(detail='Failed to sign in. Please check your email and password.', status_code=400)
    
   