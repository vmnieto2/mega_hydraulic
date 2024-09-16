from Utils.tools import Tools
from fastapi import APIRouter, Request, Depends
from Utils.decorator import http_decorator
from Class.Params import Param
from Middleware.jwt_bearer import JWTBearer

tools = Tools()
param_router = APIRouter()

@param_router.post('/params/get_type_document', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def get_type_document(request: Request):
    response = Param().get_type_document()
    return response

@param_router.post('/params/get_type_user', tags=["Params"], response_model=dict, dependencies=[Depends(JWTBearer())])
@http_decorator
def get_type_user(request: Request):
    response = Param().get_type_user()
    return response
