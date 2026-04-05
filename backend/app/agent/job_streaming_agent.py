from langchain.agents import create_agent
from app.services.llm_service import llm_service
from app.tools import JOB_TOOLS
from app.agent.job_agent_runtime import shared_job_checkpointer


class JobStreamingAgent:
    def __init__(self):
        self.model = llm_service.get_client()
        self.checkpointer = shared_job_checkpointer

        self.agent = create_agent(
            model=self.model,
            tools=JOB_TOOLS,
            checkpointer=self.checkpointer,
            system_prompt=(
                "You are JobKG-Agent, an intelligent job recommendation assistant. "
                "You should remember the context within the same conversation thread. "
                "Use previous messages in the same thread to understand follow-up questions. "
                "The user's skills may come from either the current message or previous messages "
                "in the same thread. When the current message does not explicitly provide a full "
                "skill list, you should infer and reuse the previously established skills from the same thread. "
                "Always preserve and accumulate skills across the conversation unless the user explicitly "
                "corrects, replaces, or removes them. "
                "Your job is to help users understand which jobs fit their skills, "
                "what skills they are missing, what courses they may learn next, "
                "and how different jobs compare. "
                "Before answering, use the job task classification tool when helpful. "
                "For recommend_job tasks, prefer using the graph-based job recommendation tool. "
                "For analyze_gap tasks, prefer using the graph-based skill gap analysis tool. "
                "For recommend_course tasks, prefer using the graph-based course recommendation tool. "
                "For compare_job tasks, prefer using the compare_jobs tool. "
                "Use tool results to produce grounded answers. "
                "Answer in a clear and concise way for chat UI. "
                "Do not output JSON unless the user explicitly asks for it."
            ),
            name="job_streaming_agent",
        )

    def stream_text(self, message: str, thread_id: str):
        """
        流式返回最终回复文本。
        """
        for chunk in self.agent.stream(
            {
                "messages": [
                    {"role": "user", "content": message}
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id
                }
            },
            stream_mode="messages",
        ):
            if isinstance(chunk, tuple) and len(chunk) == 2:
                message_chunk, metadata = chunk

                text = ""

                if hasattr(message_chunk, "content"):
                    content = message_chunk.content
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        parts = []
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                parts.append(item.get("text", ""))
                        text = "".join(parts)

                if text:
                    yield text


job_streaming_agent = JobStreamingAgent()