# 这就是所有 ORM 模型的共同父类。以后你定义的 User、ChatSession 这些类都要继承它。
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass