from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#유저명 비밀번호, 주소/포트번호
engine = create_engine("mysql+pymysql://admin:1234@0.0.0.0:3306/dev")
# 만든 엔진에대한 세션생성
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# 만들어진 Base는 models에서 사용
Base = declarative_base()