from contextlib import asynccontextmanager
from config.mongoconnection import mongo_client
from config.redis import get_redis_signup, get_redis_loggedin, get_redis_blocked
from fastapi import FastAPI
import uvicorn

port = 8088


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"server is running on port:{port}")
    yield
    redis = await get_redis_signup()
    await redis.close()
    redis = await get_redis_loggedin()
    await redis.close()
    redis = await get_redis_blocked()
    await redis.close()
    print("redis closed")
    mongo_client.close()
    print("database closed")
    print(f"server is shutting down...")


def __init_app__():
    app = FastAPI(
        lifespan=lifespan,
        title="Online Judge",
        description="An Online Judge using FastAPI",
        docs_url="/docs",
    )

    @app.get('/')
    async def homePage():
        return {"success": True, "message": "welcome Home"}

    from controller.UserAuthController import router as user_route

    app.include_router(user_route)

    return app


app = __init_app__()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=port, reload=True) 
