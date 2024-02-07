from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from repository.user.UserAuthRedisRepository import UserAuthRedisRepository
from service.email.EmailService import EmailService
from utils.SignupEmailGenerator import SignUpEmailGenerator


class UserAuthRepository:
    
    @classmethod
    async def saveUser(cls, user_data: dict(), db):
        collection = db["users"]

        try:
            await collection.insert_one(user_data)
        except DuplicateKeyError as e:
            error_message = str(e)
            if "username" in error_message:
                raise HTTPException(status_code=400, detail="username already exists")
            elif "email" in error_message:
                raise HTTPException(status_code=400, detail="email already exists")

        message, data = await SignUpEmailGenerator.generateMessage(user_data.copy())
        await UserAuthRedisRepository.saveUserSignUpData(data)
        email_sender = EmailService()

        try:
            await email_sender.send_email(
                user_data.get("email"), "Online Judge Email Verification", message
            )
        except Exception as e:
            print(e)
        response = {"status": True, "status_code": 200, "message": "SignUp Successful"}
        return response

    @classmethod
    async def validateUser(cls,user_data: dict(), db):
        collection = db['users']
        try:
            await collection.update_one(
                {"username": user_data["username"]}, 
                {"$set": {
                    "isEmailVerified": True
                    }
                 })
            response = {"Success": True, "message": "User email is verified"}
            return response
        except Exception as e:
            print(f"Exception updating user email verification:{e}")

    @classmethod
    async def validateUserOtp(cls,user_data: dict(), db):
        collection = db['users']
        try:
            await collection.update_one(
                {"username": user_data["username"]}, 
                {"$set": {
                    "isEmailVerified": True
                    }
                 })
            response = {"Success": True, "message": "User email is verified"}
            return response
        except Exception as e:
            print(f"Exception updating user email verification:{e}")


    @classmethod
    async def userLogin(cls,user_data:dict(),db):
        collection= db['users']
        to_search = user_data.get('to_search')
        document = await collection.find_one({
             to_search:user_data.get(to_search)
            }, {
                'created_at':0,
                'updated_at':0,
            })
        
        return document
    
    @classmethod
    async def userLogout(cls,user_data:dict()):
        pass