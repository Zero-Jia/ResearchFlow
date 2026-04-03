from pydantic import BaseModel, Field
from app.schemas.job_report import JobRecommendationReport


class JobReportTestRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Job recommendation question")


class JobReportTestResponse(BaseModel):
    question: str
    report: JobRecommendationReport