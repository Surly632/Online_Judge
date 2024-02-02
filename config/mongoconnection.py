from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
async def get_db():
    db = mongo_client.get_database(os.getenv("DATABASE"))
    try:
        await db.command("ping")
        print(f"connected to mongodb database")
    except Exception as e:
        print(e)
    return db
