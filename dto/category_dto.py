from pydantic import BaseModel

class CategoryRequest(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    uid: str
    name: str