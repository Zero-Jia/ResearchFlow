# 这张表存任务完成后最终生成的结构化报告。
from datetime import datetime

from sqlalchemy import Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("research_tasks.id"), nullable=False, unique=True, index=True)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[str] = mapped_column(Text, nullable=True)
    comparison: Mapped[str] = mapped_column(Text, nullable=True)
    sources: Mapped[str] = mapped_column(Text, nullable=True)
    suggestions: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)