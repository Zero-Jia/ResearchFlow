from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job_report import JobRecommendationReport


class JobRecommendationRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, description="当前用户 ID，可选")
    session_id: Optional[int] = Field(default=None, description="当前会话 ID，可选")
    question: str = Field(..., min_length=1, description="职位推荐相关问题")
    skills: List[str] = Field(default_factory=list, description="结构化输入的技能列表")


class JobRecommendationResponse(BaseModel):
    normalized_skills: List[str]
    report: JobRecommendationReport