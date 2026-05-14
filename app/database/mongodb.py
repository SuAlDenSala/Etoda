from motor.motor_asyncio import AsyncIOMotorClient
import certifi  # <-- NEW: Import the certificate library
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_client = MongoDB()

async def connect_to_mongo():
    print("Connecting to MongoDB...")
    
    # NEW: Pass tlsCAFile=certifi.where() to force correct SSL verification
    db_client.client = AsyncIOMotorClient(
        settings.MONGODB_URL, 
        tlsCAFile=certifi.where()
    )
    
    db_client.db = db_client.client[settings.DATABASE_NAME]
    print("Connected successfully.")

async def close_mongo_connection():
    print("Closing MongoDB connection...")
    if db_client.client:
        db_client.client.close()