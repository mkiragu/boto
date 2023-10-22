from fastapi import FastAPI, Depends, HTTPException, UploadFile
from uuid import uuid4
from fastapi import FastAPI
from repository.users_repository import SessionLocal, User
from dto.user_dto import UserDTO
from dto.user_request import UserRequest
from sqlalchemy.orm import Session
from service.image_processor import process_nanonets_image, process_mindee_image

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/process-image/mindee")
async def process_image_mindee(image: UploadFile):
    return await process_mindee_image(image)

@app.post("/process-image/nanonet")
async def process_image_nanonet(image: UploadFile):
    return await process_nanonets_image(image)


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