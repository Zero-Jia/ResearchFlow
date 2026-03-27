from langchain.agents import create_agent
from langchain.messages import HumanMessage

from app.schemas.report import ResearchReport
from app.services.llm_service import llm_service
from app.tools import TOOLS


class StructuredResearchFlowAgent:
    def __init__(self):
        self.model = llm_service.get_client()

        self.agent = create_agent(
            model=self.model,
            tools=TOOLS,
            response_format=ResearchReport,
            system_prompt=(
                "You are ResearchFlow, an AI research assistant. "
                "Your job is to answer user questions with a structured research report. "
                "When useful, first classify the task as research, compare, summary, or general. "
                "Use tools when needed. "
                "If the task is compare-oriented, prefer using the comparison tool. "
                "If the task is research-oriented, prefer using the local research search tool. "
                "If the search result is long or the user asks for a concise note, "
                "interview answer, or engineering-style explanation, use the summarization tool. "
                "Return the final answer strictly as a structured report."
            ),
            name="structured_research_assistant",
        )

    def run(self, message: str) -> ResearchReport:
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=message)
                ]
            }
        )

        structured = result.get("structured_response")
        if structured is None:
            raise ValueError("No structured_response returned by the agent.")

        return structured


structured_researchflow_agent = StructuredResearchFlowAgent()