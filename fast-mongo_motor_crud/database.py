from motor.motor_asyncio import AsyncIOMotorClient

from config import DATABASE_URL


class MongoDB:
    def __init__(self, uri: str):
        print("흠", uri)
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client["practice_db"]

    def get_collection(self, name: str):
        return self.db[name]

    async def close(self):
        self.client.close()


# MongoDB 인스턴스 생성
mongo_instance = MongoDB(DATABASE_URL)
