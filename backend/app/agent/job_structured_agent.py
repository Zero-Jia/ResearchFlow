from langchain.agents import create_agent
from langchain.messages import HumanMessage

from app.schemas.job_report import JobRecommendationReport
from app.services.llm_service import llm_service
from app.tools import JOB_TOOLS


class JobStructuredAgent:
    def __init__(self):
        self.model = llm_service.get_client()

        self.agent = create_agent(
            model=self.model,
            tools=JOB_TOOLS,
            response_format=JobRecommendationReport,
            system_prompt=(
                "You are JobKG-Agent, an intelligent job recommendation assistant. "
                "Your job is to help users understand which jobs may fit their skills, "
                "what skills they are missing, what courses they may learn next, "
                "and how different jobs compare. "
                "Before answering, use the job task classification tool when helpful "
                "to determine whether the request is recommend_job, analyze_gap, "
                "recommend_course, compare_job, or general_career_question. "
                "At this stage, external job graph tools are not available yet, "
                "so keep recommendations conservative and structured. "
                "If the user's input includes skills, place them into input_skills. "
                "If exact recommendations are uncertain, keep recommended_jobs empty "
                "and provide reasonable suggestions. "
                "Return the final answer strictly as a structured object."
            ),
        )

    def run(self, message: str) -> JobRecommendationReport:
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=message)
                ]
            }
        )

        structured = result.get("structured_response")
        if structured is None:
            raise ValueError("No structured_response returned by the job structured agent.")

        return structured


job_structured_agent = JobStructuredAgent()