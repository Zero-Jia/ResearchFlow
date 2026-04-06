from typing import Any

from langgraph.graph import MessagesState


class JobGraphState(MessagesState):
    session_id: int
    current_question: str
    conversation_text: str

    # 新增：允许外部传入最近历史消息，后续可由 chat route / service 填充
    history_messages: list[dict[str, Any]]
    previous_skills: list[str]
    merged_skills: list[str]

    task_type: str
    plan: list[str]

    recommend_result: dict[str, Any]
    gap_result: dict[str, Any]
    course_result: dict[str, list[str]]
    compare_result: dict[str, Any]

    # 新增：记忆修正结果 / fallback 结果
    memory_result: dict[str, Any]
    fallback_result: dict[str, Any]

    report: dict[str, Any]
    answer_text: str

    reasoning: list[str]
    latest_reasoning: str