from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine

# DB에서 models에서 정의한 테이블(User)를 생성하겠다는 의미
# 앱실행시 테이블이 자동으로 만들어진다.
models.Base.metadata.create_all(bind=engine)


app = FastAPI()

# DB를 사용하기 위한 일종의 helper 함수
def get_db():
    db = SessionLocal()
    try:
        # return은 반환하고 함수가 끝나지만, yield는 반환하고 함수가 끝나지 않는다
        yield db
    finally:
        db.close()


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existed_user = db.query(models.User).filter_by(
        email=user.email
    ).first()

    if existed_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(email=user.email, password=user.password)
    db.add(user)
    db.commit()

    return user


@app.get("/users", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()