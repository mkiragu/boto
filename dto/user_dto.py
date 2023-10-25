from pydantic import BaseModel

class UserDTO(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    gender: str
    age: int