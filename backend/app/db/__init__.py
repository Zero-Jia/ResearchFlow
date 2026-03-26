from app.core.config import settings


# 把.env 里的 MySQL 配置拼成 SQLAlchemy 能识别的数据库连接字符串。
def get_database_url() -> str:
    return (
        f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
        f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}?charset=utf8mb4"
    )