import io
import tempfile
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from mindee import Client
from mindee.documents import TypeReceiptV5
from uuid import uuid4
from fastapi import FastAPI
from repository.users_repository import SessionLocal, User
from dto.user_dto import UserDTO
from dto.user_request import UserRequest
from sqlalchemy.orm import Session

import os
from dotenv import load_dotenv
load_dotenv()
mindee_api_key = os.getenv("MINDEE_API_KEY")
mindee_client = Client(api_key=mindee_api_key)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}", response_model=UserDTO)
async def get_user_info(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=UserDTO)
async def create_user(request: UserRequest, db: Session = Depends(get_db)):
    
	# Transform UserRequest into a User model
    user_model = User(
        id=str(uuid4()),
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        age=request.age
    )
    
	# Check if the username or email is already in use
    existing_user = db.query(User).filter(
        User.username == user_model.username or User.email == user_model.email
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already in use")

    # Create and add the new user to the database
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    # Create a UserDTO object from the created user's data
    user_dto = UserDTO(
        username=user_model.username,
        email=user_model.email
    )

    return user_dto

@app.post("/process-image/")
async def process_image(image: UploadFile):
    try:
        # Read the image data from the UploadFile object
        image_data = await image.read()

        # Create a temporary file and write the image data to it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(image_data)

        # Create a Mindee document from the temporary file
        input_doc = mindee_client.doc_from_path(temp_file.name)
        
        # Replace "TypeReceiptV5" with the appropriate parsing type
        result = input_doc.parse(TypeReceiptV5)

        # Process the parsed data or return it as needed
        return {"parsed_data": result.document}

    except Exception as e:
        return {"error": str(e)}