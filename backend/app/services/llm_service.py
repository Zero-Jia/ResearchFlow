from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings


class LLMService:
    def __init__(self):
        self.client = ChatOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )

    def get_client(self) -> ChatOpenAI:
        return self.client

    def chat(self, message: str) -> str:
        messages = [
            SystemMessage(
                content=(
                    "You are ResearchFlow, an AI research assistant. "
                    "You should provide clear, accurate, and structured answers."
                )
            ),
            HumanMessage(content=message),
        ]
        response = self.client.invoke(messages)
        return response.content


llm_service = LLMService()