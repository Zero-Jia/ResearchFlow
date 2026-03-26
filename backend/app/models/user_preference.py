# 这张表是用户级的长期偏好配置，后面 Agent 生成 prompt 时会直接依赖它。
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)

    output_style: Mapped[str] = mapped_column(String(50), nullable=False, default="technical")
    output_language: Mapped[str] = mapped_column(String(20), nullable=False, default="zh")
    output_format: Mapped[str] = mapped_column(String(50), nullable=False, default="summary_first")
    focus_preference: Mapped[str] = mapped_column(String(100), nullable=False, default="engineering")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)