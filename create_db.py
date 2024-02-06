from config.mongoconnection import get_db
import asyncio


async def create_db():
    db = await get_db()
    try:
        db.drop_collection('users')
    except Exception as e:
        print('collection does not exist')
    finally:
        print('collection droped')
    collection = db["users"]
    try:
        await collection.create_index([("first_name", 1)], sparse=True)
        await collection.create_index([("last_name", 1)], sparse=True)
        await collection.create_index([("username", 1)], unique=True, sparse=True)
        await collection.create_index([("userid", 1)], unique=True, sparse=True)
        await collection.create_index([("email", 1)], unique=True, sparse=True)
        await collection.create_index([("password", 1)], sparse=True)
        await collection.create_index([("phone_number", 1)])
        await collection.create_index([("address", 1)])
        await collection.create_index([("t_shirt_size", 1)])
        await collection.create_index([("bio", 1)])
        await collection.create_index([("facebook_id", 1)])
        await collection.create_index([("codeforces_id", 1)])
        await collection.create_index([("status", 1)],sparse=True)
        await collection.create_index([("isEmailVerified", 1)],sparse=True)
        await collection.create_index([("isActivated", 1)])
        # await collection.create_index([("isLoggedIn", 1)],sparse=True)
        # await collection.create_index([("deviceInfo", 1)],sparse=True)
        await collection.create_index([("role", 1)],sparse=True)
        await collection.create_index([("updated_at", 1)],sparse=True)

        
        print('indexes created')

    finally:        
        db.client.close()
        print('databse closed')


asyncio.run(create_db())
