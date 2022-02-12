from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from decouple import config

#유저명 비밀번호, 주소/포트번호
engine = create_engine(f"mysql+pymysql://{config('DB_USER')}:{config('DB_PWD')}@localhost:3306/dev")
# 만든 엔진에대한 세션생성
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# 만들어진 Base는 models에서 사용
Base = declarative_base()