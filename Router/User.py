from Utils.tools import Tools
from fastapi import APIRouter, Request
from Utils.decorator import http_decorator
from Class.User import User
from Schemas.user import User as UserSchema

tools = Tools()
user_router = APIRouter()

@user_router.post('/login', tags=["Auth"], response_model=dict,)
@http_decorator
def login(request: Request, user: UserSchema):
    data = getattr(request.state, "json_data", {})
    response = User().login(data)
    return response
