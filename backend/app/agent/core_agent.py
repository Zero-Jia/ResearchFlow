from langchain.agents import create_agent
from langchain.messages import HumanMessage

from app.services.llm_service import llm_service
from app.tools import RESEARCH_TOOLS


class ResearchFlowAgent:
    def __init__(self):
        self.model = llm_service.get_client()

        self.agent = create_agent(
            model=self.model,
            tools=RESEARCH_TOOLS,
            system_prompt=(
                "You are ResearchFlow, an AI research assistant. "
                "Help the user with research-related questions. "
                "When useful, first classify the user's task to understand whether it is "
                "a research task, compare task, summary task, or general task. "
                "If it is a compare task, prefer using the comparison tool. "
                "If it is a research task, prefer using the local research search tool. "
                "If search results are long or the user asks for a concise note, "
                "interview answer, or engineering-style explanation, then use the summarization tool. "
                "When the user asks about the project name, use the appropriate tool. "
                "When the user asks about the agent role or responsibility, use the appropriate tool. "
                "Keep the final answer clear, concise, and grounded in tool results when available."
            ),
            name="research_assistant",
        )

    def run(self, message: str) -> str:
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=message)
                ]
            }
        )

        messages = result["messages"]
        last_message = messages[-1]
        content = last_message.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            return "\n".join([p for p in text_parts if p]).strip()

        return str(content)


researchflow_agent = ResearchFlowAgent()