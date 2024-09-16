from jwt import encode, decode
import os
from dotenv import load_dotenv

load_dotenv()

def create_token(data: dict):
    token = encode(payload=data, key=os.getenv("MY_SECRET_KEY"), algorithm="HS256")
    return token

def validate_token(token: str) -> dict:
    data: dict = decode(token, key=os.getenv("MY_SECRET_KEY"), algorithms=["HS256"])
    return data
