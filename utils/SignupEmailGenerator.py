import pyotp
import secrets
from itsdangerous import URLSafeTimedSerializer
from repository.user.UserAuthRedisRepository import UserAuthRedisRepository

'''
This became tight coupling because I generated otp and the link here,
Should do loose coupling.
'''
class SignUpEmailGenerator:
    @staticmethod
    async def generateMessage(user_data):
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
        token = secrets.token_hex(9)
        serializer = URLSafeTimedSerializer(token)
        encoded_data = serializer.dumps(
            {"username": user_data.get("username"), "email": user_data.get("email")}
        )
        link = f"http://localhost:8088/users/validate?user={encoded_data}"
        
        message = f"""
        Hello {user_data.get('first_name')} {user_data.get('last_name')}, welcome to the online judge.
        Please verify your account by confirming the email. 
        Your otp is :{otp}
        or click the link below to verify the account: {link}
        
        Please note that this email or otp is valid for only 5 minutes.
        
        Regards,
        Online Judge Team
        """
        data={
            'username': user_data.get('username'),
            'secret_key':token,
            'otp':otp,
            'link':encoded_data
        }
        return message,data
