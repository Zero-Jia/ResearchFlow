from pydantic import BaseModel, Field
from app.schemas.report import ResearchReport


class ReportTestRequest(BaseModel):
    question: str = Field(..., min_length=1, description="研究型输入问题")


class ReportTestResponse(BaseModel):
    question: str
    report: ResearchReport