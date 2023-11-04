from fastapi import HTTPException

error_code = '05ff9572-f7f0-4c72-b6ab-b1b875c43ada'

class ResourceNotFoundException(HTTPException):
    def __init__(self):
        detail = error_code
        super().__init__(status_code=400, detail=detail)