from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job_report import JobRecommendationReport


class CreateJobTaskRequest(BaseModel):
    user_id: int = Field(..., description="当前用户 ID")
    session_id: int = Field(..., description="当前会话 ID")
    question: str = Field(..., min_length=1, description="职位推荐问题")
    skills: List[str] = Field(default_factory=list, description="用户输入的技能列表")


class CreateJobTaskResponse(BaseModel):
    task_id: int
    status: str
    normalized_skills: List[str]
    report: JobRecommendationReport


class JobTaskSummaryItem(BaseModel):
    task_id: int
    task_type: str
    topic: str
    status: str
    created_at: str


class JobTaskHistoryResponse(BaseModel):
    items: List[JobTaskSummaryItem]


class JobTaskDetailResponse(BaseModel):
    task_id: int
    user_id: int
    session_id: int
    task_type: str
    topic: str
    user_input: str
    status: str
    normalized_skills: List[str]
    created_at: str
    updated_at: str
    report: Optional[JobRecommendationReport] = None