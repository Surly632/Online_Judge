import aioredis
from dotenv import load_dotenv
import os

load_dotenv()


async def get_redis_signup():
    url = os.getenv("REDIS_URL_SIGNUP_VALIDATION")

    if not url:
        raise ValueError("REDIS_URL_SIGNUP_VALIDATION environment variable is not set.")

    redis = await aioredis.from_url(url)
    return redis


async def get_redis_loggedin():
    url = os.getenv("REDIS_URL_LOGGED_IN")

    if not url:
        raise ValueError("REDIS_URL_LOGGED_IN environment variable is not set.")

    redis = await aioredis.from_url(url)
    return redis


async def get_redis_blocked():
    url = os.getenv("REDIS_URL_BLOCKED_USER")

    if not url:
        raise ValueError("REDIS_URL_BLOCKED_USER environment variable is not set.")

    redis = await aioredis.from_url(url)
    return redis
