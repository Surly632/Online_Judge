from fastapi import APIRouter, Depends, Request
from config.JwtBearer import JwtBearer
from config.mongoconnection import get_db
from model.user.UserModel import Users

from service.user.UserAuthService import UserAuthService

router = APIRouter(prefix="/users")


@router.post("/create")
async def signUp(request: Users, db = Depends(get_db)):
    return await UserAuthService.createUser(request, db)


@router.get("/validate")
async def validateUser(req: Request, db = Depends(get_db)):
    user_data = req.query_params.get("user")
    print(f"user validation link: {user_data}")
    return await UserAuthService.validateUser(user_data, db)


@router.post("/validate-user-otp")
async def validateUserOtp(request: Request, db= Depends(get_db)):
    otp = await request.json()
    otp = otp.get("otp")
    # print(f'otp from controller: {otp}')
    return await UserAuthService.validateUserOtp(otp, db)


@router.post("/login")
async def userLogin(request: Request, db = Depends(get_db)):
    user_data = await request.json()
    return await UserAuthService.userLogin(user_data, db)


@router.delete(
    "/logout",
    dependencies=[Depends(JwtBearer(required_roles=["admin", "SuperAdmin", "User"]))],
)
async def userLogout(request: Request):
    token = request.headers.get("Authorization")
    token = token.split("Bearer ")[-1]
    return await UserAuthService.userLogout(token)


@router.get(
    "/userdetails",
    dependencies=[Depends(JwtBearer(required_roles=["admin", "SuperAdmin", "User"]))],
)
async def userdetails(req: Request):
    authorization = req.headers.get("Authorization")
    token = authorization.split("Bearer ")[-1]
    return token


@router.get(
    "/regenerate-token",
    dependencies=[Depends(JwtBearer(required_roles=["admin", "SuperAdmin", "User"]))],
)
async def regenerateToken(req: Request):
    
    refreshToken = req.json()
    refreshToken = refreshToken.get('refreshToken')
    
    return await UserAuthService.regenerateToken(refreshToken)
