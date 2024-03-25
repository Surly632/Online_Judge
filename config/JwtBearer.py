import os
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import jwt
from starlette.requests import Request
from dotenv import load_dotenv

from config.redis import get_redis_blocked_token

load_dotenv()


class JwtBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True, required_roles: list[str] = None):
        super(JwtBearer, self).__init__(auto_error=auto_error)
        self.required_roles = required_roles or ["User"]

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credentials: HTTPAuthorizationCredentials = await super(
            JwtBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid Authentication Scheme"
                )
            verify_status = await self.verify_status(credentials.credentials)
            if not verify_status:
                raise HTTPException(status_code=403, detail="Token is not valid")

            elif verify_status:
                return credentials.credentials

            else:
                raise HTTPException(status_code=403, detail="Invalid Token")

        else:
            raise HTTPException(
                status_code=403, detail="Authentication scheme not found!"
            )


async def verify_status(self, token: str):
   
    reids = await get_redis_blocked_token()
    if await reids.exists(token):
        raise HTTPException(status_code=403, detail="Token is blocked")

    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=["HS512"], audience="oj"
        )
        if payload:
            role_in_token = payload.get("role")
            if role_in_token in self.required_roles:
                return True
            else:
                raise HTTPException(
                    status_code=403, detail="Insufficient role permissions"
                )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
