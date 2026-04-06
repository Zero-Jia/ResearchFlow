from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END

from app.core.config import settings
from app.graph.job_graph_state import JobGraphState
from app.tools.job_tools import (
    classify_job_task_core,
    plan_task_core,
    recommend_jobs_core,
    analyze_skill_gap_core,
    recommend_courses_core,
    compare_jobs_core,
    _extract_job_names_from_text,
    merge_skills_with_correction,
    build_memory_update_result,
)


def _append_reasoning(state: JobGraphState, text: str) -> dict:
    old = state.get("reasoning", []) or []
    return {
        "reasoning": old + [text],
        "latest_reasoning": text,
    }


def _message_to_text(msg) -> str:
    if isinstance(msg, dict):
        return (msg.get("content") or "").strip()
    content = getattr(msg, "content", "")
    return content.strip() if isinstance(content, str) else ""


llm = init_chat_model(
    model=settings.LLM_MODEL,
    model_provider="openai",
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0.3,
)


def prepare_context_node(state: JobGraphState):
    """
    这版先兼容两种来源：
    1. history_messages: 由后端路由显式传入最近历史消息
    2. messages: 当前 graph 调用时传入的消息列表

    后续你把 chat route / chat service 发我后，
    我再帮你把“按 session_id 查最近消息”接进来。
    """
    history_messages = state.get("history_messages", []) or []
    current_messages = state.get("messages", []) or []

    conversation_parts = []

    for item in history_messages[-10:]:
        if isinstance(item, dict):
            role = item.get("role", "")
            content = (item.get("content") or "").strip()
            if content:
                conversation_parts.append(f"{role}: {content}")

    for item in current_messages[-6:]:
        content = _message_to_text(item)
        if content:
            conversation_parts.append(content)

    current_question = ""
    if current_messages:
        current_question = _message_to_text(current_messages[-1])

    history_text = "\n".join(conversation_parts[:-1]) if conversation_parts else ""
    conversation_text = "\n".join(conversation_parts).strip()

    # 先从历史对话中恢复已有技能
    previous_skills = state.get("previous_skills", []) or []

    # 如果外部没传 previous_skills，就退化为从历史文本里提取
    # 注意：这里不直接使用旧版 extract_skills_from_question，
    # 因为我们希望后续统一走 merge_skills_with_correction
    if not previous_skills and history_text:
        previous_skills = merge_skills_with_correction([], history_text)

    # 再结合当前输入做修正/新增
    merged_skills = merge_skills_with_correction(previous_skills, current_question)

    update = {
        "current_question": current_question,
        "conversation_text": conversation_text,
        "previous_skills": previous_skills,
        "merged_skills": merged_skills,
    }
    update.update(
        _append_reasoning(
            state,
            f"已结合历史上下文与当前输入，整理技能集合：{', '.join(merged_skills) if merged_skills else '无'}",
        )
    )
    return update


def planner_node(state: JobGraphState):
    task_type = classify_job_task_core(state.get("current_question", "") or state.get("conversation_text", ""))
    plan = plan_task_core(task_type)

    update = {
        "task_type": task_type,
        "plan": plan,
    }
    update.update(
        _append_reasoning(
            state,
            f"Planner 已判定任务类型为 {task_type}，执行计划为：{' -> '.join(plan)}",
        )
    )
    return update


def route_from_planner(
    state: JobGraphState,
) -> Literal["recommend", "gap", "course", "compare", "memory_update", "fallback_llm"]:
    task_type = state.get("task_type", "fallback_llm")

    if task_type in ["recommend_job", "general_career_question"]:
        return "recommend"
    if task_type == "analyze_gap":
        return "gap"
    if task_type == "recommend_course":
        return "course"
    if task_type == "compare_job":
        return "compare"
    if task_type == "memory_update":
        return "memory_update"
    return "fallback_llm"


def recommend_node(state: JobGraphState):
    skills_text = "、".join(state.get("merged_skills", []))
    result = recommend_jobs_core(skills_text)

    update = {"recommend_result": result}
    update.update(
        _append_reasoning(
            state,
            f"已完成岗位推荐，得到岗位：{', '.join(result.get('recommended_jobs', [])) if result.get('recommended_jobs') else '无'}",
        )
    )
    return update


def gap_node(state: JobGraphState):
    question_text = state.get("conversation_text", "")
    job_names = _extract_job_names_from_text(question_text)

    if not job_names:
        recommend_result = state.get("recommend_result", {}) or {}
        top_jobs = recommend_result.get("recommended_jobs", [])
        target_job = top_jobs[0] if top_jobs else ""
    else:
        target_job = job_names[0]

    if not target_job:
        result = {"job_name": "", "matched_skills": [], "missing_skills": []}
        update = {"gap_result": result}
        update.update(_append_reasoning(state, "未识别到明确目标岗位，暂时跳过技能差距分析"))
        return update

    skills_text = "、".join(state.get("merged_skills", []))
    result = analyze_skill_gap_core(target_job, skills_text)

    update = {"gap_result": result}
    update.update(_append_reasoning(state, f"已完成技能差距分析，目标岗位：{target_job}"))
    return update


def course_node(state: JobGraphState):
    target_skills = []

    gap_result = state.get("gap_result", {}) or {}
    if gap_result.get("missing_skills"):
        target_skills = gap_result["missing_skills"]

    if not target_skills:
        recommend_result = state.get("recommend_result", {}) or {}
        recommended_jobs = recommend_result.get("recommended_jobs", [])
        missing_map = recommend_result.get("missing_skills", {})
        if recommended_jobs:
            top_job = recommended_jobs[0]
            target_skills = missing_map.get(top_job, [])

    # 如果连缺失技能都没有，就不要直接拿 merged_skills 去推荐课程
    # 否则“我会 Python、Pandas”会被误当成“我想学 Python、Pandas”
    skills_text = "、".join(target_skills) if target_skills else ""
    result = recommend_courses_core(skills_text) if skills_text else {}

    update = {"course_result": result}
    update.update(
        _append_reasoning(
            state,
            f"已完成课程推荐，目标技能：{', '.join(target_skills) if target_skills else '无'}",
        )
    )
    return update


def compare_node(state: JobGraphState):
    question_text = state.get("conversation_text", "")
    job_names = _extract_job_names_from_text(question_text)

    if len(job_names) < 2:
        result = {
            "comparison": "未能从当前问题中识别出两个明确岗位，因此暂时无法完成对比。",
            "fit": {},
        }
        update = {"compare_result": result}
        update.update(_append_reasoning(state, "岗位对比跳过：未识别到两个岗位"))
        return update

    skills_text = "、".join(state.get("merged_skills", []))
    result = compare_jobs_core(job_names[0], job_names[1], skills_text)

    update = {"compare_result": result}
    update.update(_append_reasoning(state, f"已完成岗位对比：{job_names[0]} vs {job_names[1]}"))
    return update


def memory_update_node(state: JobGraphState):
    current_question = state.get("current_question", "")
    previous_skills = state.get("previous_skills", []) or []

    result = build_memory_update_result(previous_skills, current_question)

    update = {
        "memory_result": result,
        "merged_skills": result.get("current_skills", []),
    }
    update.update(
        _append_reasoning(
            state,
            f"已完成技能记忆修正，新增：{', '.join(result.get('added_skills', [])) if result.get('added_skills') else '无'}；"
            f"移除：{', '.join(result.get('removed_skills', [])) if result.get('removed_skills') else '无'}",
        )
    )
    return update


def fallback_llm_node(state: JobGraphState):
    current_question = state.get("current_question", "")
    merged_skills = state.get("merged_skills", []) or []
    conversation_text = state.get("conversation_text", "") or ""

    prompt = f"""
你是一个职业规划助手。

当前用户技能记忆：
{merged_skills}

最近对话上下文：
{conversation_text}

当前问题：
{current_question}

请直接用自然中文回答。
要求：
1. 优先结合上下文与技能记忆；
2. 如果用户是在纠正技能，请先承认并说明你更新后的理解；
3. 不要强行做岗位推荐；
4. 不要编造知识图谱事实；
5. 如果这是开放式追问，就给自然、贴题的建议；
6. 不要答非所问；
7. 不要输出 JSON。
"""

    answer = llm.invoke(prompt)
    answer_text = answer.content if isinstance(answer.content, str) else str(answer.content)

    update = {
        "fallback_result": {"answer": answer_text},
        "answer_text": answer_text,
        "messages": [AIMessage(content=answer_text)],
    }
    update.update(_append_reasoning(state, "当前问题更适合开放式回答，已转入 fallback_llm"))
    return update


def summarize_node(state: JobGraphState):
    task_type = state.get("task_type", "fallback_llm")
    merged_skills = state.get("merged_skills", []) or []

    if task_type == "memory_update":
        memory_res = state.get("memory_result", {}) or {}
        factual_report = {
            "task_type": task_type,
            "input_skills": memory_res.get("current_skills", []),
            "previous_skills": memory_res.get("previous_skills", []),
            "current_skills": memory_res.get("current_skills", []),
            "added_skills": memory_res.get("added_skills", []),
            "removed_skills": memory_res.get("removed_skills", []),
            "message": memory_res.get("message", ""),
        }

        prompt = f"""
你是一个职业规划助手。
下面是用户技能记忆更新结果：
{factual_report}

请生成自然中文回答。
要求：
1. 先说明你已经理解用户是在纠正技能信息；
2. 明确告诉用户当前你认为他会哪些技能；
3. 如果用户问“我还有什么技能”，只回答当前记忆里的技能，不要强行推荐岗位；
4. 不要编造不存在的技能；
5. 风格自然，不要输出 JSON。
"""
        answer = llm.invoke(prompt)
        answer_text = answer.content if isinstance(answer.content, str) else str(answer.content)

        update = {
            "report": factual_report,
            "answer_text": answer_text,
            "messages": [AIMessage(content=answer_text)],
        }
        update.update(_append_reasoning(state, "已完成记忆修正结果总结"))
        return update

    recommended_jobs = []
    job_match_scores = {}
    matched_skills = {}
    missing_skills = {}
    comparison = None
    course_recommendations = {}

    if task_type in ["recommend_job", "general_career_question"]:
        rec = state.get("recommend_result", {}) or {}
        recommended_jobs = rec.get("recommended_jobs", [])
        job_match_scores = rec.get("job_match_scores", {})
        matched_skills = rec.get("matched_skills", {})
        missing_skills = rec.get("missing_skills", {})
        course_recommendations = state.get("course_result", {}) or {}

    elif task_type == "analyze_gap":
        gap = state.get("gap_result", {}) or {}
        if gap.get("job_name"):
            recommended_jobs = [gap["job_name"]]
            matched_skills = {gap["job_name"]: gap.get("matched_skills", [])}
            missing_skills = {gap["job_name"]: gap.get("missing_skills", [])}
        course_recommendations = state.get("course_result", {}) or {}

    elif task_type == "recommend_course":
        course_recommendations = state.get("course_result", {}) or {}

    elif task_type == "compare_job":
        cmp_res = state.get("compare_result", {}) or {}
        comparison = cmp_res.get("comparison")
        fit = cmp_res.get("fit", {})
        for job_name, fit_data in fit.items():
            recommended_jobs.append(job_name)
            job_match_scores[job_name] = fit_data.get("score", 0.0)
            matched_skills[job_name] = fit_data.get("matched", [])
            missing_skills[job_name] = fit_data.get("missing", [])

    factual_report = {
        "task_type": task_type,
        "input_skills": merged_skills,
        "recommended_jobs": recommended_jobs,
        "job_match_scores": job_match_scores,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "course_recommendations": course_recommendations,
        "comparison": comparison,
    }

    prompt = f"""
你是一个职业推荐智能助手。下面是已经通过知识图谱和规则工具得到的事实结果：
{factual_report}

请你基于这些事实，生成一段自然、清晰、结构化的中文回答。
要求：
1. 不能编造新的岗位、技能、课程事实；
2. 可以对已有事实做总结、解释和建议；
3. 如果是岗位推荐，输出推荐岗位、匹配点、技能缺口、课程建议和总体建议；
4. 如果是岗位对比，输出对比结论、差异点、当前更适合哪个方向以及建议；
5. 如果课程推荐为空，不要硬写课程建议；
6. 不要输出 JSON；
7. 不要答非所问；
8. 风格像一个真正的 AI 助手。
"""

    answer = llm.invoke(prompt)
    answer_text = answer.content if isinstance(answer.content, str) else str(answer.content)

    update = {
        "report": factual_report,
        "answer_text": answer_text,
        "messages": [AIMessage(content=answer_text)],
    }
    update.update(_append_reasoning(state, "已完成最终总结与建议生成"))
    return update


builder = StateGraph(JobGraphState)

builder.add_node("prepare_context", prepare_context_node)
builder.add_node("planner", planner_node)
builder.add_node("recommend", recommend_node)
builder.add_node("gap", gap_node)
builder.add_node("course", course_node)
builder.add_node("compare", compare_node)
builder.add_node("memory_update", memory_update_node)
builder.add_node("fallback_llm", fallback_llm_node)
builder.add_node("summarize", summarize_node)

builder.add_edge(START, "prepare_context")
builder.add_edge("prepare_context", "planner")

builder.add_conditional_edges(
    "planner",
    route_from_planner,
    {
        "recommend": "recommend",
        "gap": "gap",
        "course": "course",
        "compare": "compare",
        "memory_update": "memory_update",
        "fallback_llm": "fallback_llm",
    },
)

builder.add_edge("recommend", "course")
builder.add_edge("gap", "course")
builder.add_edge("course", "summarize")
builder.add_edge("compare", "summarize")
builder.add_edge("memory_update", "summarize")
builder.add_edge("fallback_llm", END)
builder.add_edge("summarize", END)

job_graph_app = builder.compile()