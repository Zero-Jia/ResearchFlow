from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.job_report import JobRecommendationReport


class ChatSessionCreateRequest(BaseModel):
    title: Optional[str] = Field(default="新会话")


class ChatSessionItem(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str


class ChatSessionListResponse(BaseModel):
    items: List[ChatSessionItem]


class ChatMessageItem(BaseModel):
    id: int
    role: str
    content: str
    created_at: str


class ChatMessageListResponse(BaseModel):
    session_id: int
    messages: List[ChatMessageItem]


class ChatSendRequest(BaseModel):
    question: str = Field(..., min_length=1)
    skills: List[str] = Field(default_factory=list)


class ChatSendResponse(BaseModel):
    session_id: int
    user_message: ChatMessageItem
    assistant_message: ChatMessageItem
    report: JobRecommendationReport