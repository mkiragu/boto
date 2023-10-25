from pydantic import BaseModel
from typing import Optional

class SigninRequest(BaseModel):
    email: str
    password: str