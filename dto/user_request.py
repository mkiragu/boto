from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    age: Optional[int]