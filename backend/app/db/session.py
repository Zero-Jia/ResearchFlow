'''
第一，engine 是数据库连接引擎。
第二，SessionLocal 是数据库会话工厂，以后每次接口操作数据库都从这里拿 session。
第三，get_db() 是给 FastAPI 用的依赖注入函数，后面接口里可以直接 Depends(get_db)。
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session

from app.db import get_database_url

DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit = False,
    bind=engine
)

def get_db():
    db:Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()