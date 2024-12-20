from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()


class JwtService:

    @classmethod
    async def generateAccessToken(cls, data: dict, time_delta: Optional[timedelta] = None ):
        to_encode = data.copy()
        if time_delta:
            to_encode.update({"exp": datetime.utcnow() + time_delta})
        else:
            to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=15)})
        try:
            token = jwt.encode(
                to_encode, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM")
            )
            return token
        except Exception as e:
            print(f"Token generation exception at jwt_service{e}")
            return {}
        
    @classmethod
    async def generateRefreshToken(cls, data: dict, time_delta: Optional[timedelta] = None ):
        to_encode = data.copy()
        if time_delta:
            to_encode.update({"exp": datetime.utcnow() + time_delta})
        else:
            to_encode.update({"exp": datetime.utcnow() + timedelta(days=30)})
        try:
            token = jwt.encode(
                to_encode, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM")
            )
            return token
        except Exception as e:
            print(f"Token generation exception at jwt_service{e}")
            return {}

    @classmethod
    async def decodeToken(cls, token: str):
        try:
            data = jwt.decode(
                token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"), audience="oj"
            )
            return data
        except Exception as e:
            print(f"Decode token exception: {e}")
            return {}
