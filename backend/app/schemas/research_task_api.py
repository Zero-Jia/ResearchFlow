from typing import List, Optional
from pydantic import BaseModel, Field


class CreateResearchTaskRequest(BaseModel):
    user_id: int = Field(..., description="当前用户 ID")
    session_id: int = Field(..., description="当前会话 ID")
    question: str = Field(..., min_length=1, description="用户研究问题")


class ResearchTaskSummaryItem(BaseModel):
    task_id: int
    task_type: str
    topic: str
    status: str
    created_at: str


class ReportData(BaseModel):
    summary: str
    key_points: List[str]
    comparison: Optional[str] = None
    suggestions: List[str]


class CreateResearchTaskResponse(BaseModel):
    task_id: int
    task_type: str
    topic: str
    status: str
    report: ReportData


class ResearchTaskDetailResponse(BaseModel):
    task_id: int
    user_id: int
    session_id: int
    task_type: str
    topic: str
    user_input: str
    status: str
    created_at: str
    updated_at: str
    report: Optional[ReportData] = None


class ResearchTaskHistoryResponse(BaseModel):
    items: List[ResearchTaskSummaryItem]