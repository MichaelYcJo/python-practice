from dataclasses import asdict
from typing import Any

import pymongo
from motor.motor_asyncio import AsyncIOMotorCollection

from app.entities.category.category_codes import CategoryCode
from app.entities.collections.geo_json import GeoJsonPoint, GeoJsonPolygon
from app.entities.collections.shop.shop_document import (
    ShopDeliveryAreaSubDocument,
    ShopDocument,
)
from app.utils.mongo import db


class ShopCollection:
    _collection = AsyncIOMotorCollection(db, "shops")

    """
    첫 번째 매개변수 ("delivery_areas.poly"):
        •	이 부분은 인덱스를 설정할 필드 이름입니다.
        •	즉, 여기서는 delivery_areas라는 필드의 하위 필드인 poly에 대해 인덱스를 생성하겠다는 의미입니다.
        2.	두 번째 매개변수 (pymongo.GEOSPHERE):
        •	이 부분은 인덱스의 타입을 나타냅니다.
        •	pymongo.GEOSPHERE는 지리적 구면 좌표 인덱스를 뜻하며, MongoDB에서 제공하는 지리적 쿼리를 효율적으로 처리할 수 있도록 설정하는 특별한 인덱스 타입입니다.
        •	이 타입은 **구 좌표계(지구 표면을 기준으로 하는 좌표)**를 기반으로 거리 계산을 하거나, 특정 범위 내에 있는 위치를 검색하는 데 사용됩니다.
        
        compass > explain plan > {'delivery_areas.poly': {$geoIntersects: { $geometry: { type: 'Point', coordinates: [ 126.9234, 37.611 ] }}}}
    """

    @classmethod
    async def set_index(self) -> None:
        await self._collection.create_index([("delivery_areas.poly", pymongo.GEOSPHERE)])

    @classmethod
    async def get_distinct_category_codes_by_point_intersects(cls, point: GeoJsonPoint) -> list[CategoryCode]:
        return [
            CategoryCode(category_code)
            for category_code in await cls._collection.distinct(
                "category_codes",
                {"delivery_areas.poly": {"$geoIntersects": {"$geometry": asdict(point)}}},
            )
        ]

    @classmethod
    async def point_intersects(cls, point: GeoJsonPoint) -> list[ShopDocument]:
        return [
            cls._parse(result)
            #  $geoIntersects -> “delivery_areas.poly 폴리곤과 point 가 서로 겹치면, 그 document 를 가져옴”
            for result in await cls._collection.find(
                {"delivery_areas.poly": {"$geoIntersects": {"$geometry": asdict(point)}}}
            ).to_list(length=None)
        ]

    @classmethod
    async def insert_one(
        cls, name: str, category_codes: list[CategoryCode], delivery_areas: list[ShopDeliveryAreaSubDocument]
    ) -> ShopDocument:
        result = await cls._collection.insert_one(
            {
                "name": name,
                "category_codes": category_codes,
                "delivery_areas": [asdict(delivery_area) for delivery_area in delivery_areas],
            }
        )

        return ShopDocument(
            _id=result.inserted_id, name=name, category_codes=category_codes, delivery_areas=delivery_areas
        )

    @classmethod
    def _parse(cls, result: dict[Any, Any]) -> ShopDocument:
        return ShopDocument(
            _id=result["_id"],
            name=result["name"],
            delivery_areas=[
                ShopDeliveryAreaSubDocument(poly=GeoJsonPolygon(coordinates=delivery_area["poly"]["coordinates"]))
                for delivery_area in result["delivery_areas"]
            ],
            category_codes=[CategoryCode(category_code) for category_code in result["category_codes"]],
        )
