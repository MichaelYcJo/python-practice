from typing import List


from fastapi import Depends, FastAPI, Form, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models, schemas
from .database import SessionLocal, engine

# DB에서 models에서 정의한 테이블(User)를 생성하겠다는 의미
# 앱실행시 테이블이 자동으로 만들어진다.
models.Base.metadata.create_all(bind=engine)


app = FastAPI()
# mount : static파일을 import하게해줌. 주소는 /static static에 디렉토리를 잡아주면된다.
app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}


@app.post("/file/size")
def get_filesize(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/file/info")
async def get_file_info(file: UploadFile = File(...)):
    file_like_obj = file.file
    contents = await file.read()

    return {
        "content_type": file.content_type,
        "filename": file.filename,
    }
    

from tempfile import NamedTemporaryFile
from typing import IO
    
async def save_file(file: IO):
    # s3 업로드라고 생각해 봅시다. delete=True(기본값)이면
    # 현재 함수가 닫히고 파일도 지워집니다.
    with NamedTemporaryFile("wb", delete=False) as tempfile:
        tempfile.write(file.read())
        return tempfile.name


@app.post("/file/store")
async def store_file(file: UploadFile = File(...)):
    path = await save_file(file.file)
    return {"filepath": path}


class SomeError(Exception):
    def __init__(self, name: str, code: int):
        self.name = name
        self.code = code

    def __str__(self):
        return f"<{self.name}> is occured. code: <{self.code}>"

@app.exception_handler(SomeError)
async def some_error_handler(request: Request, exc: SomeError):
    return JSONResponse(
        content={"message": f"error is {exc.name}"}, status_code=exc.code
    )

@app.get("/error")
async def get_error():
    raise SomeError("500 error!", 500)