from fastapi import FastAPI
from mangum import Mangum
from routers import router


PRE_FIX_URL = "/test"


app = FastAPI()
app.include_router(router.router, prefix=PRE_FIX_URL)


@app.get("/")
def read_root() -> dict:
    return {"status": "ok"}


handler = Mangum(app, lifespan="off")
