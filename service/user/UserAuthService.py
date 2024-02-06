"""
Created By: Surly
"""

import json
import bcrypt
from fastapi import HTTPException
import pytz
from datetime import datetime
from config.redis import get_redis_login
from model.user.UserModel import Users
from repository.user.UserAuthRedisRepository import UserAuthRedisRepository
from repository.user.UserAuthRepository import UserAuthRepository
from service.Jwt.JwtService import JwtService


timezone = pytz.timezone("Asia/Dhaka")


class UserAuthService:

    @classmethod
    async def createUser(cls, user_data: Users, db):

        user_data = user_data.dict()
        passcode = user_data.get("password").encode("utf-8")
        passcode = bcrypt.hashpw(passcode, bcrypt.gensalt())
        user_data.update({"password": passcode.decode("utf-8")})

        created_at = datetime.now(timezone)
        updated_at = datetime.now(timezone)
        user_data.update({"created_at": created_at, "updated_at": updated_at})

        """
        Tight coupling here, Should Make another class in utils 
        to generate token and validator link 
        """

        return await UserAuthRepository.saveUser(user_data, db)

    @classmethod
    async def validateUser(cls, url: str, db):
        data = await UserAuthRedisRepository.validateUser(url)
        # print(f'link_data: {json.loads(data)}')
        if data is None:
            raise HTTPException(status_code=404, detail="URL Time expired")
        return await UserAuthRepository.validateUser(json.loads(data), db)

    @classmethod
    async def validateUserOtp(cls, otp: str, db):
        print(f"otp from service:{otp}")
        data = await UserAuthRedisRepository.validateUserOtp(otp)
        # print(f'link_data: {json.loads(data)}')
        if data is None:
            raise HTTPException(status_code=404, detail="URL Time expired bro!")
        return await UserAuthRepository.validateUserOtp(json.loads(data), db)

    @classmethod
    async def userLogin(cls, user_data: dict(), db):

        user = user_data.get("username", -1)

        if user == -1:
            user = user_data.get("email")
            to_search = user
            user_data.update({"to_search": "email"})
        else:
            to_search = user_data.get("username")
            user_data.update({"to_search": "username"})

        document = await UserAuthRepository.userLogin(user_data, db)

        if document:
            document.update({"_id": str(document["_id"])})
        else:
            return HTTPException(status_code=404, detail="user not found!")

        db_password = document.get("password").encode("utf-8")
        given_password = user_data.get("password").encode("utf-8")

        password_match = bcrypt.checkpw(given_password, db_password)

        redis = await get_redis_login()

        if not password_match:

            mismatched_times = await redis.incr(to_search)
            # await redis.flushdb()
            print(f"mismatched_times:{mismatched_times}")
            await redis.expire(to_search, 180)
            if mismatched_times >= 3:
                await redis.expire(to_search, 900)
                return HTTPException(
                    status_code=429,
                    detail="You entered wrong credentials many times. Try again after some time.",
                )

            return HTTPException(
                status_code=401,
                detail=f"Wrong Credentials. You have {3-mismatched_times} try left",
            )

        elif password_match:

            in_redis = await redis.exists(to_search)
            mismatched_times =0
            if in_redis:
                mismatched_times = await redis.get(to_search)
                mismatched_times = int(mismatched_times.decode('utf-8'))
                print(f'mismatched_times:{mismatched_times}')

            if mismatched_times < 3 and in_redis:

                await redis.delete(to_search)

                data = {
                'id': str(document.get('_id')),
                'sub':document.get('username'),
                'role':document.get('role'),
                'aud':'oj',
                 }

                token= await JwtService.generateToken(data)

                return {
                    'success':True,
                    'status_code':200,
                    'message':'User login successful',
                    'token':token,
                    }

            elif mismatched_times>=3 and in_redis:
                return HTTPException(
                    status_code=429,
                    detail="You entered wrong credentials many times. Try again after some time."
                )

            else:

                data = {
                    'id': str(document.get('_id')),
                    'sub':document.get('username'),
                    'role':document.get('role'),
                    'aud':'oj'
                }
                token= await JwtService.generateToken(data)
                return {
                        'success':True,
                        'status_code':200,
                        'message':'User login successful',
                        'token':token,
                        }

    @classmethod
    async def userLogout(cls,token: str):
        user_data =await JwtService.decodeToken(token)
        is_successful = await UserAuthRedisRepository.userLogout(token,user_data.get('sub'))
        print(f'is_successful: {is_successful}')
        if is_successful:
            return {
                "status_code": 204,
                "success": True,
                "message": "User logout successful",
            }
        else:
            return HTTPException(status_code=500,detail='Internal Server Error')
        
    @classmethod
    async def regenerateToken(token:str):
        user_data = await JwtService.decodeToken(token)
        return await JwtService.generateToken(user_data)