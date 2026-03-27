from pydantic import BaseModel, Field


class CompareTestRequest(BaseModel):
    question: str = Field(..., min_length=1, description="对比型问题输入")


class CompareTestResponse(BaseModel):
    question: str
    answer: str