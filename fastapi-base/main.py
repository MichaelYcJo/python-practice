import uvicorn

from enum import Enum
from fastapi import FastAPI, Request
from typing import Optional


app = FastAPI()

class UserLevel(str, Enum):
    a = "a"
    b = "b"
    c = "c"


@app.get("/")
def hello():
    return "Hello, Worsld!"


@app.get("/users")
def get_users(grade: UserLevel = UserLevel.a, limit: Optional[int] = None):
    context = {
        "grade": grade,
        "limit": limit
    }

    return context

@app.get("/users/{user_id:int}")
def get_user(user_id: float, request: Request):
    print(request.path_params)  # {'user_id': 123} 출력
    return {"user_id": user_id}  # {"user_id": 123.0} 응답


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)