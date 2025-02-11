from fastapi import FastAPI

from app.apis.category.v1.home_category_router import router as home_category_router
from app.entities.collections import set_indexes

app = FastAPI()

app.include_router(home_category_router)


# fastapi 가 시작할 때마다 인댁스를 생성(app.on_event(), asgi.py를 실행하면 인덱스가 생성되는걸 볼 수있음)
# python asgi.py
@app.on_event("startup")
async def on_startup() -> None:
    await set_indexes()
