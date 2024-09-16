from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException
from Utils.jwt_manager import validate_token
from Utils.querys import Querys

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        data_user = Querys().get_user(data["email"])
        if data["email"] != data_user.email:
            raise HTTPException(status_code=400, detail="Credenciales invalidas")
