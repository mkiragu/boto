from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    age: Optional[int]
    gender: Optional[str]