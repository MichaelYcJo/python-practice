from dataclasses import asdict

from motor.motor_asyncio import AsyncIOMotorCollection

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.shop.shop_document import (
    ShopDeliveryAreaSubDocument,
    ShopDocument,
)
from app.utils.mongo import db


class ShopCollection:
    _collection = AsyncIOMotorCollection(db, "shops")

    @classmethod
    async def insert_one(
        cls, name: str, category_codes: list[CategoryCode], delivery_areas: list[ShopDeliveryAreaSubDocument]
    ) -> ShopDocument:
        ...
