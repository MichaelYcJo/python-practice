import asyncio
from asyncio import AbstractEventLoop
from typing import Generator

import pytest_asyncio

from app.utils.mongo import db


@pytest_asyncio.fixture(scope="session", autouse=False)
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    print("session scope 실행")
    loop = asyncio.new_event_loop()
    yield loop
    print("session scope 종료")
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db() -> None:
    print("function scope 실행")
    for collection_name in await db.list_collection_names():
        await db[collection_name].drop()
