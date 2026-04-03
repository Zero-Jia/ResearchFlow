from pydantic import BaseModel, Field


class JobTestRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Job recommendation question")


class JobTestResponse(BaseModel):
    message: str