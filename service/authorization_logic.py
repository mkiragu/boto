from fastapi import Header
from fastapi.exceptions import HTTPException
from typing import Annotated
from firebase_admin import auth

def authorize_user(authorization: Annotated[str | None, Header()] = None):
    try:
        if authorization:
            decoded_token = auth.verify_id_token(authorization)
            # You can use the `decoded_token` for user authorization
            return decoded_token
        else:
            raise HTTPException(detail='Authorization token is missing', status_code=401)
    except auth.ExpiredIdTokenError:
        raise HTTPException(detail='JWT token has expired', status_code=401)
    except auth.InvalidIdTokenError:
        raise HTTPException(detail='Invalid JWT token', status_code=401)
    except Exception as e:
        raise HTTPException(detail=f'Authorization Error: {str(e)}', status_code=401)