from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MONGO_DATABASE, MONGO_URL

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DATABASE]
