# 初始化建表脚本
from app.db.base import Base
from app.db.session import engine

from app.models import *

def init_db():
    # 根据你定义好的 ORM 模型，把表真正创建到 MySQL。
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")

if __name__ == "__main__":
    init_db()