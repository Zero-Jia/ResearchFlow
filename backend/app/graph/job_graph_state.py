from typing import Any

from langgraph.graph import MessagesState


class JobGraphState(MessagesState):
    session_id: int
    current_question: str
    conversation_text: str

    history_messages: list[dict[str, Any]]
    previous_skills: list[str]
    merged_skills: list[str]

    task_type: str
    plan: list[str]
    planner_source: str

    recommend_result: dict[str, Any]
    gap_result: dict[str, Any]
    course_result: dict[str, list[str]]
    compare_result: dict[str, Any]

    memory_result: dict[str, Any]
    fallback_result: dict[str, Any]

    report: dict[str, Any]
    answer_text: str

    reasoning: list[str]
    latest_reasoning: str

    # 新增：技能更新过程记录
    skill_update_source: str
    skill_update_added: list[str]
    skill_update_removed: list[str]