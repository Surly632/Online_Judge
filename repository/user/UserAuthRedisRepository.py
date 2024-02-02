import json

from config.redis import get_redis_signup

class UserAuthRedisRepository:
    @classmethod
    async def saveUserSignUpData(cls,user_data:dict()):
        redis = await get_redis_signup()
        try:
            await redis.setex(user_data.get('link'),300,json.dumps(user_data).encode('utf-8'));
            await redis.setex(user_data.get('otp'),300,json.dumps(user_data).encode('utf-8'));
            print(f'redis size: {await redis.dbsize()}')
        except Exception as e:
            print(f'''Exception:{e}''')
   
    @classmethod
    async def validateUser(cls,url:str):
        redis = await get_redis_signup()
        try:
            print(f'url:{url}')
            data = await redis.get(url)
            return data     
        except Exception as e:
            print(f'exception from auth redis validate user: {e}')
        
    @classmethod
    async def validateUserOtp(cls, otp:str):
        redis = await get_redis_signup()
        try:
            print(f'otp from auth-redis :{otp}')
            data = await redis.get(otp)
            return data     
        except Exception as e:
            print(f'exception from auth redis validate user: {e}')
        