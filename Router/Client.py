from Utils.tools import Tools
from fastapi import APIRouter, Request
from Utils.decorator import http_decorator
from Class.Client import Client

tools = Tools()
client_router = APIRouter()

@client_router.post('/client/create', tags=["Client"], response_model=dict)
@http_decorator
def create_client(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Client().create_client(data)
    return response

@client_router.post('/client/list_client', tags=["Client"], response_model=dict)
@http_decorator
def list_client(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Client().list_client(data)
    return response

@client_router.post('/client/update_client', tags=["Client"], response_model=dict)
@http_decorator
def update_client(request: Request):
    data = getattr(request.state, "json_data", {})
    response = Client().update_client(data)
    return response
