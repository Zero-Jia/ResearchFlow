#这一步的核心意义是：把所有模型统一导入，确保后面 Base.metadata.create_all() 能拿到完整表信息。
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.research_task import ResearchTask
from app.models.research_report import ResearchReport
from app.models.user_preference import UserPreference

__all__ = [
    "User",
    "ChatSession",
    "ChatMessage",
    "ResearchTask",
    "ResearchReport",
    "UserPreference",
]