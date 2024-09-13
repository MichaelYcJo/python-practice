import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import MONGO_URL, MONGO_DATABASE

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DATABASE]


async def print_mongo_version():
    status = await client.test.command("serverStatus")
    print(status["version"])


asyncio.run(print_mongo_version())
