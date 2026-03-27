from pydantic import BaseModel, Field


class AgentTestRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户发送给 Agent 的消息")


class AgentTestResponse(BaseModel):
    user_message: str
    agent_message: str