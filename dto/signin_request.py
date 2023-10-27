from pydantic import BaseModel

class SigninRequest(BaseModel):
    email: str
    password: str