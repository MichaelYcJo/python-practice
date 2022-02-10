from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl


app = FastAPI()


class User(BaseModel):
    name: str = "fastapi"
    password: str
    avatar_url: HttpUrl = None


@app.post(
    "/include",
    response_model=User,
    response_model_include={"name", "avatar_url"},  # Set 타입. List도 괜찮습니다.
)
def get_user_with_include(user: User):
    return user


@app.post(
    "/exclude",
    response_model=User,
    response_model_exclude={"password"},
)
def get_user_with_exclude(user: User):
    return user


@app.post(
    "/unset",
    response_model=User,
    response_model_exclude_unset=True,
)
def get_user_with_exclude_unset(user: User):
    return user