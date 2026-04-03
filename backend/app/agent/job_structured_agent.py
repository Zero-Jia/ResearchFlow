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
                "Your job is to help users understand which jobs fit their skills, "
                "what skills they are missing, and what courses they may learn next. "
                "Before answering, use the job task classification tool when helpful. "
                "For recommend_job tasks, prefer using the graph-based job recommendation tool. "
                "For analyze_gap tasks, prefer using the graph-based skill gap analysis tool. "
                "For recommend_course tasks, prefer using the graph-based course recommendation tool. "
                "Use tool results to produce grounded and structured outputs. "
                "If the user's input includes skills, place them into input_skills. "
                "For recommend_job tasks, try to fill recommended_jobs, job_match_scores, "
                "matched_skills, and missing_skills whenever possible. "
                "For recommend_course tasks, try to fill course_recommendations whenever possible. "
                "Return the final answer strictly as a structured object."
            ),
            name="job_structured_agent",
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