from pydantic import BaseModel, Field


class ResearchTestRequest(BaseModel):
    question: str = Field(..., min_length=1, description="研究型问题输入")


class ResearchTestResponse(BaseModel):
    question: str
    answer: str