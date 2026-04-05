from langchain.agents import create_agent
from langchain.messages import HumanMessage

from app.agent.job_agent_runtime import shared_job_checkpointer
from app.schemas.job_report import JobRecommendationReport
from app.services.llm_service import llm_service
from app.tools import JOB_TOOLS


class JobMemoryAgent:
    def __init__(self):
        self.model = llm_service.get_client()
        self.checkpointer = shared_job_checkpointer

        self.agent = create_agent(
            model=self.model,
            tools=JOB_TOOLS,
            response_format=JobRecommendationReport,
            checkpointer=self.checkpointer,
            system_prompt=(
                "You are JobKG-Agent, an intelligent job recommendation assistant. "
                "You should remember the context within the same conversation thread. "
                "Use previous messages in the same thread to understand follow-up questions. "

                "The user's skills may come from either the current message or previous messages in the same thread. "
                "When the current message does not explicitly provide a full skill list, you MUST infer and reuse the previously established skills from the same thread. "
                "Always preserve and accumulate skills across the conversation unless the user explicitly corrects, replaces, or removes them. "
                "Do NOT overwrite previously established skills with vague role names or topic words from the current turn. "
                "For example, words like '数据分析师', '后端开发', or '数据分析' are usually target roles or directions, not the user's existing skills. "

                "Your job is to help users understand which jobs fit their skills, "
                "what skills they are missing, what courses they may learn next, "
                "and how different jobs compare. "

                "Before answering, use the job task classification tool when helpful. "
                "For recommend_job tasks, prefer using the graph-based job recommendation tool. "
                "For analyze_gap tasks, prefer using the graph-based skill gap analysis tool. "
                "For recommend_course tasks, prefer using the graph-based course recommendation tool. "
                "For compare_job tasks, prefer using the compare_jobs tool. "

                "Use tool results to produce grounded and structured outputs. "

                "For input_skills, you MUST prioritize the accumulated user skills already established in the conversation. "
                "Only add newly mentioned skills if the user explicitly provides them in the current turn. "
                "If the current turn contains no new concrete skills, keep using the previously accumulated skills. "

                "For recommend_job tasks, try to fill recommended_jobs, job_match_scores, "
                "matched_skills, and missing_skills whenever possible. "
                "For recommend_course tasks, try to fill course_recommendations whenever possible. "
                "For compare_job tasks, fill comparison and suggestions whenever possible. "
                "For analyze_gap tasks, the missing skills should be analyzed against the user's accumulated real skills, not just the current question wording. "

                "Return the final answer strictly as a structured object."
            ),
            name="job_memory_agent",
        )

    def run(self, message: str, thread_id: str) -> JobRecommendationReport:
        result = self.agent.invoke(
            {
                "messages": [
                    HumanMessage(content=message)
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            }
        )

        structured = result.get("structured_response")
        if structured is None:
            raise ValueError("No structured_response returned by the memory agent.")

        return structured


job_memory_agent = JobMemoryAgent()