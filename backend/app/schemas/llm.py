from pydantic import BaseModel, Field

class LLMTestRequest(BaseModel):
    message: str = Field(..., min_length=1)

class LLMTestResponse(BaseModel):
    user_message: str
    ai_message: str
    model: str