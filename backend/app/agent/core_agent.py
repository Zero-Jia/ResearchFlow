from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from app.services.llm_service import llm_service
from app.tools.simple_tools import TOOLS


class ResearchFlowAgent:
    def __init__(self):
        self.model = llm_service.get_client()

        self.agent = create_agent(
            model=self.model,
            tools=TOOLS,
            system_prompt=(
                "You are ResearchFlow, an AI research assistant. "
                "Help the user with research-related questions. "
                "When the user asks about the project name, use the appropriate tool. "
                "When the user asks about the agent role or responsibility, use the appropriate tool. "
                "If no tool is needed, answer directly. "
                "Keep the answer clear and concise."
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