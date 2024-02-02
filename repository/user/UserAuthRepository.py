import bcrypt
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from config.redis import get_redis_loggedin
from repository.user.UserAuthRedisRepository import UserAuthRedisRepository
from service.Jwt.JwtService import JwtService

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
    
    '''
    Need a bit more work, If I use redis, need to check redis first
    '''
    @classmethod
    async def userLogin(cls,user_data:dict(),db):
        collection= db['users']
        to_search = user_data.get('to_search')
        given_password = user_data.get('password').encode('utf-8')
        document = await collection.find_one({
             to_search:user_data.get(to_search)
            }, {
                'created_at':0,
                'updated_at':0,
            })
        # print(f'user found:{document}')
        if document:
            
            document.update({'_id':str(document.get('_id'))})
            db_password = document.get('password').encode('utf-8')
            document.pop('password')
            password_match = bcrypt.checkpw(given_password,db_password)
            
            data = {
                'iss':'Online_judge',
                'sub':document.get('username'),
                'aud':'oju',
                'role':document.get('role')
            }
            
            if password_match:
                token = await JwtService.generateToken(document)
                data.update({'token':token})
                
                '''
                Logged in user kept in redis, for login from only 1 browser.
                Do we even need redis? I am forcing it lol
                '''
                
                try:
                    redis = await get_redis_loggedin()
                    await redis.set(document.get('username'),'ok')
                    user = await redis.get(document.get('username'))
                    counter+=1
                    print(f'''user: {user.decode("utf-8")},
                          total:{await redis.dbsize()},
                          
                          ''')
                except Exception as e:
                    print(f'Exception from userauthlogin:{e}')
                    
                return data
            else:
                raise HTTPException(status_code=404,detail='Wrong credentials')
        else:
            return {'success':False,'message':'No user found!'}