from langchain.agents import create_agent
from langchain.messages import HumanMessage

from app.schemas.job_report import JobRecommendationReport
from app.services.llm_service import llm_service


class JobStructuredAgent:
    def __init__(self):
        self.model = llm_service.get_client()

        self.agent = create_agent(
            model=self.model,
            tools=[],
            response_format=JobRecommendationReport,
            system_prompt=(
                "You are JobKG-Agent, an intelligent job recommendation assistant. "
                "Your job is to help users understand which jobs may fit their skills, "
                "what skills they are missing, and what courses they may learn next. "
                "At this stage, no external job graph tools are available yet, so you should "
                "infer the user's task type from the question and return a structured job recommendation report. "
                "If the user's input includes skills, place them into input_skills. "
                "If exact recommendations are uncertain, keep recommended_jobs empty and provide conservative suggestions. "
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