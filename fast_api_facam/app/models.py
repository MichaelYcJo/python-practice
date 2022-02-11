from sqlalchemy import Boolean, Column, Integer, String

from .database import Base

# 데이터베이스의 Base를 상속받아서 User를 만든다.
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    is_active = Column(Boolean, default=True)