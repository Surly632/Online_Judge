"""
Created By: Surly
"""

import json
import bcrypt
from fastapi import HTTPException
import pytz
from datetime import datetime
from model.user.UserModel import Users
from repository.user.UserAuthRedisRepository import UserAuthRedisRepository
from repository.user.UserAuthRepository import UserAuthRepository


timezone = pytz.timezone("Asia/Dhaka")


class UserAuthService:
    @classmethod
    async def createUser(cls,user_data: Users, db):
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
    async def validateUser(cls,url:str, db):
        data = await UserAuthRedisRepository.validateUser(url)
        # print(f'link_data: {json.loads(data)}')
        if data is None:
            raise HTTPException(status_code=404,detail='URL Time expired')
        return await UserAuthRepository.validateUser(json.loads(data),db)
    
    @classmethod
    async def validateUserOtp(cls, otp:str, db):
        print(f'otp from service:{otp}')
        data = await UserAuthRedisRepository.validateUserOtp(otp)
        # print(f'link_data: {json.loads(data)}')
        if data is None:
            raise HTTPException(status_code=404,detail='URL Time expired bro!')
        return await UserAuthRepository.validateUserOtp(json.loads(data), db)
    
    
    @classmethod
    async def userLogin(cls,user_data:dict(), db):
        
        user=user_data.get('username',-1)
        if user == -1:
            user = user_data.get('email')
            user_data.update({'to_search':'email'})
        else:
            user_data.update({'to_search':'username'})
        user_data.update({'user':user})
        return await UserAuthRepository.userLogin(user_data,db)
    