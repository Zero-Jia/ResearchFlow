from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END

from app.core.config import settings
from app.graph.job_graph_state import JobGraphState
from app.tools.job_tools import (
    classify_job_task_core,
    normalize_task_type,
    plan_task_core,
    recommend_jobs_core,
    analyze_skill_gap_core,
    recommend_courses_core,
    compare_jobs_core,
    _extract_job_names_from_text,
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


def classify_job_task_by_llm(question: str, conversation_text: str = "") -> str:
    prompt = f"""
你是一个职业规划系统中的“任务分类器”。

请根据用户当前问题以及最近对话上下文，将任务分类为以下 7 种之一：
- recommend_job
- analyze_gap
- recommend_course
- compare_job
- general_career_question
- memory_update
- fallback_llm

分类标准：
1. recommend_job
   - 用户想知道适合什么岗位、推荐什么工作、有哪些适合自己的职位
2. analyze_gap
   - 用户围绕某个岗位问“我还差什么技能”“技能差距是什么”
3. recommend_course
   - 用户明确要学习建议、课程推荐、学习路径
4. compare_job
   - 用户要比较两个岗位、问区别、哪个更适合
5. general_career_question
   - 用户在问职业方向、发展路径、有哪些方向可选
6. memory_update
   - 用户在纠正自己的技能信息，或在问“你记得我会什么 / 我的技能有哪些”
7. fallback_llm
   - 开放式追问，不适合直接进入图谱推荐/分析流程，例如面试建议、简历建议、怎么准备

要求：
- 只能输出一个标签
- 不要解释
- 不要输出 JSON
- 不要输出多余文字

最近对话上下文：
{conversation_text}

当前问题：
{question}
"""
    try:
        answer = llm.invoke(prompt)
        raw = answer.content if isinstance(answer.content, str) else str(answer.content)
        return normalize_task_type(raw)
    except Exception:
        return ""


def prepare_context_node(state: JobGraphState):
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

    previous_skills = state.get("previous_skills", []) or []

    # 没有外部传入 previous_skills 时，尝试从历史文本恢复一次
    if not previous_skills and history_text:
        history_memory_result = build_memory_update_result([], history_text)
        previous_skills = history_memory_result.get("current_skills", [])

    memory_result = build_memory_update_result(previous_skills, current_question)
    merged_skills = memory_result.get("current_skills", previous_skills)

    update = {
        "current_question": current_question,
        "conversation_text": conversation_text,
        "previous_skills": previous_skills,
        "merged_skills": merged_skills,
        "skill_update_source": memory_result.get("update_source", "unknown"),
        "skill_update_added": memory_result.get("added_skills", []),
        "skill_update_removed": memory_result.get("removed_skills", []),
    }
    update.update(
        _append_reasoning(
            state,
            f"已结合历史上下文与当前输入更新技能集合："
            f"当前技能={', '.join(merged_skills) if merged_skills else '无'}；"
            f"新增={', '.join(memory_result.get('added_skills', [])) if memory_result.get('added_skills') else '无'}；"
            f"移除={', '.join(memory_result.get('removed_skills', [])) if memory_result.get('removed_skills') else '无'}；"
            f"来源={memory_result.get('update_source', 'unknown')}",
        )
    )
    return update


def planner_node(state: JobGraphState):
    current_question = state.get("current_question", "") or state.get("conversation_text", "")
    conversation_text = state.get("conversation_text", "") or ""

    llm_task_type = classify_job_task_by_llm(current_question, conversation_text)

    if llm_task_type:
        task_type = llm_task_type
        planner_source = "llm_classifier"
    else:
        task_type = classify_job_task_core(current_question)
        planner_source = "rule_fallback"

    plan = plan_task_core(task_type)

    update = {
        "task_type": task_type,
        "plan": plan,
        "planner_source": planner_source,
    }
    update.update(
        _append_reasoning(
            state,
            f"Planner 已判定任务类型为 {task_type}，来源：{planner_source}，执行计划为：{' -> '.join(plan)}",
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
        "skill_update_source": result.get("update_source", "unknown"),
        "skill_update_added": result.get("added_skills", []),
        "skill_update_removed": result.get("removed_skills", []),
    }
    update.update(
        _append_reasoning(
            state,
            f"已完成技能记忆修正，新增：{', '.join(result.get('added_skills', [])) if result.get('added_skills') else '无'}；"
            f"移除：{', '.join(result.get('removed_skills', [])) if result.get('removed_skills') else '无'}；"
            f"来源：{result.get('update_source', 'unknown')}",
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
            "update_source": memory_res.get("update_source", ""),
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