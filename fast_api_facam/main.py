from enum import Enum

from fastapi import FastAPI

app = FastAPI()

class UserLevel(str, Enum):
    a = "a"
    b = "b"
    c = "c"


@app.get("/users")
def get_users(grade: UserLevel):
    return {"grade": grade}