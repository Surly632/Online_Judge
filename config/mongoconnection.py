from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

async def get_db()->AsyncIOMotorClient:
    mongo_client =  AsyncIOMotorClient(os.getenv("MONGO_URL"))
    db = mongo_client.get_database(os.getenv("DATABASE"))
    try:
        yield db
    except Exception as e:
        print(e)
    finally:
        mongo_client.close()
        
