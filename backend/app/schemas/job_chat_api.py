from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job_report import JobRecommendationReport


class JobChatRequest(BaseModel):
    session_id: int = Field(..., description="会话 ID，同一个 session_id 会共享短期记忆")
    user_id: Optional[int] = Field(default=None, description="用户 ID，可选")
    question: str = Field(..., min_length=1, description="本轮用户问题")
    skills: List[str] = Field(default_factory=list, description="本轮显式传入的技能列表，可为空")


class JobChatResponse(BaseModel):
    session_id: int
    normalized_skills: List[str]
    report: JobRecommendationReport