import json
import re
from typing import Any

from langchain.chat_models import init_chat_model
from langchain.tools import tool

from app.core.config import settings
from app.services.graph_service import graph_service
from app.services.user_profile_service import user_profile_service


ALLOWED_TASK_TYPES = {
    "recommend_job",
    "analyze_gap",
    "recommend_course",
    "compare_job",
    "general_career_question",
    "memory_update",
    "fallback_llm",
}


llm = init_chat_model(
    model=settings.LLM_MODEL,
    model_provider="openai",
    api_key=settings.LLM_API_KEY,
    base_url=settings.LLM_BASE_URL,
    temperature=0.1,
)


def _extract_skills_from_text(text: str) -> list[str]:
    if not text:
        return []
    return user_profile_service.extract_skills_from_question(text)


def _normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def _safe_get_all_skills() -> list[str]:
    """
    尽量从图谱服务里拿到全量技能名称。
    如果 graph_service 暂时没有 get_all_skills()，就退化为：
    从所有岗位的 required_skills 中汇总。
    """
    try:
        if hasattr(graph_service, "get_all_skills"):
            raw_skills = graph_service.get_all_skills() or []
            results = []

            for item in raw_skills:
                if isinstance(item, dict):
                    name = item.get("name")
                    if name:
                        results.append(str(name))
                elif item:
                    results.append(str(item))

            return sorted(list(set(results)))
    except Exception:
        pass

    try:
        jobs = graph_service.get_jobs_with_required_skills() or []
        skills = set()
        for job in jobs:
            for skill in job.get("required_skills", []):
                if skill:
                    skills.add(str(skill))
        return sorted(list(skills))
    except Exception:
        return []


def _normalize_and_filter_skills(skills: list[str]) -> list[str]:
    """
    统一技能名称，并过滤掉不在图谱技能表中的项，避免 LLM 幻觉。
    """
    normalized = user_profile_service.normalize_skills(skills or [])
    all_skills = set(_safe_get_all_skills())
    if not all_skills:
        return normalized
    return [skill for skill in normalized if skill in all_skills]


def _extract_job_names_from_text(text: str) -> list[str]:
    if not text:
        return []

    text_lower = text.lower()
    all_jobs = graph_service.get_all_jobs()
    found = []

    for job in all_jobs:
        name = job["name"]
        if name.lower() in text_lower and name not in found:
            found.append(name)

    return found


def _calculate_job_match_score(
    user_skills: list[str],
    required_skills: list[str],
) -> tuple[float, list[str], list[str]]:
    matched = [skill for skill in required_skills if skill in user_skills]
    missing = [skill for skill in required_skills if skill not in user_skills]

    if not required_skills:
        return 0.0, matched, missing

    coverage_score = len(matched) / len(required_skills)

    core_skills = required_skills[:2]
    core_matched = [skill for skill in core_skills if skill in user_skills]
    core_score = len(core_matched) / len(core_skills) if core_skills else 0.0

    final_score = round(0.7 * coverage_score + 0.3 * core_score, 2)
    return final_score, matched, missing


def _extract_positive_skills_from_text(text: str) -> list[str]:
    return _extract_skills_from_text(text)


def _extract_negative_skills_from_text(text: str) -> list[str]:
    """
    规则版负向技能抽取（fallback 用）
    """
    if not text:
        return []

    text_norm = _normalize_text(text)
    all_skills = _safe_get_all_skills()
    if not all_skills:
        return []

    negative_skills = []
    negative_patterns = [
        r"不会",
        r"没有",
        r"不懂",
        r"不熟",
        r"不是我的技能",
        r"不是我会的",
        r"去掉",
        r"删掉",
        r"删除",
        r"移除",
        r"去除",
        r"纠正",
        r"记错",
    ]

    has_negative_signal = any(re.search(pattern, text_norm) for pattern in negative_patterns)
    if not has_negative_signal:
        return []

    for skill_name in all_skills:
        skill_lower = skill_name.lower()
        if skill_lower in text_norm:
            negative_skills.append(skill_name)

    return sorted(list(set(negative_skills)))


def extract_skill_updates_rule_based(
    previous_skills: list[str],
    current_text: str,
) -> dict[str, Any]:
    """
    规则版技能更新：作为 LLM 技能抽取失败时的兜底。
    """
    previous_skills = sorted(list(set(previous_skills or [])))

    positive_skills = _normalize_and_filter_skills(_extract_positive_skills_from_text(current_text))
    negative_skills = _normalize_and_filter_skills(_extract_negative_skills_from_text(current_text))

    skill_set = set(previous_skills)

    for skill in negative_skills:
        if skill in skill_set:
            skill_set.remove(skill)

    for skill in positive_skills:
        if skill not in negative_skills:
            skill_set.add(skill)

    current_skills = sorted(list(skill_set))
    removed_skills = [skill for skill in previous_skills if skill not in current_skills]
    added_skills = [skill for skill in current_skills if skill not in previous_skills]

    return {
        "previous_skills": previous_skills,
        "current_skills": current_skills,
        "added_skills": added_skills,
        "removed_skills": removed_skills,
        "message": "已根据当前输入更新技能记忆。",
        "update_source": "rule_fallback",
    }


def normalize_task_type(raw: str) -> str:
    if not raw:
        return ""

    text = str(raw).strip()

    if text in ALLOWED_TASK_TYPES:
        return text

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            task_type = str(data.get("task_type", "")).strip()
            if task_type in ALLOWED_TASK_TYPES:
                return task_type
    except Exception:
        pass

    for task_type in ALLOWED_TASK_TYPES:
        if task_type in text:
            return task_type

    return ""


def normalize_skill_update_output(raw: str) -> dict[str, list[str]]:
    """
    将 LLM 的技能更新输出标准化为：
    {
      "added_skills": [...],
      "removed_skills": [...]
    }
    """
    empty = {"added_skills": [], "removed_skills": []}
    if not raw:
        return empty

    text = str(raw).strip()

    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            return empty

        added = data.get("added_skills", [])
        removed = data.get("removed_skills", [])

        if not isinstance(added, list):
            added = []
        if not isinstance(removed, list):
            removed = []

        return {
            "added_skills": [str(x).strip() for x in added if str(x).strip()],
            "removed_skills": [str(x).strip() for x in removed if str(x).strip()],
        }
    except Exception:
        return empty


def extract_skill_updates_by_llm(
    previous_skills: list[str],
    current_text: str,
) -> dict[str, Any]:
    """
    用 LLM 从用户当前输入中抽取技能增删变化。
    只抽取“用户明确表达自己会/不会/补充/纠正”的技能，
    不要把岗位名、目标方向、职业名称误判为技能。
    """
    previous_skills = sorted(list(set(previous_skills or [])))
    all_skills = _safe_get_all_skills()

    prompt = f"""
你是一个“用户技能记忆更新器”。

你的任务是：根据“用户当前输入”，判断用户是否在这句话里明确表达了：
1. 新增了自己会的技能
2. 删除了自己不会/不具备/需要纠正掉的技能

你只能输出 JSON，格式固定如下：
{{
  "added_skills": ["技能1", "技能2"],
  "removed_skills": ["技能3"]
}}

规则：
1. 只抽取“用户明确声称自己拥有或不拥有”的技能。
2. 不要把岗位名、职业方向、目标职位当作技能。
3. 像“数据分析师”“后端开发工程师”“产品经理”默认是岗位，不是技能。
4. 用户如果只是问“哪个岗位更适合我”“我想做某岗位”，不要新增技能。
5. 如果没有明确技能变化，就返回空列表。
6. 只能使用候选技能列表中的技能名，不要编造新技能。
7. 不要输出解释，不要输出 markdown，只输出 JSON。

当前已记住的技能：
{previous_skills}

候选技能列表：
{all_skills}

用户当前输入：
{current_text}
"""
    answer = llm.invoke(prompt)
    raw = answer.content if isinstance(answer.content, str) else str(answer.content)
    parsed = normalize_skill_update_output(raw)

    added_skills = _normalize_and_filter_skills(parsed.get("added_skills", []))
    removed_skills = _normalize_and_filter_skills(parsed.get("removed_skills", []))

    skill_set = set(previous_skills)

    for skill in removed_skills:
        if skill in skill_set:
            skill_set.remove(skill)

    for skill in added_skills:
        if skill not in removed_skills:
            skill_set.add(skill)

    current_skills = sorted(list(skill_set))

    return {
        "previous_skills": previous_skills,
        "current_skills": current_skills,
        "added_skills": [skill for skill in current_skills if skill not in previous_skills],
        "removed_skills": [skill for skill in previous_skills if skill not in current_skills],
        "message": "已根据当前输入更新技能记忆。",
        "update_source": "llm_extractor",
    }


def merge_skills_with_correction(
    previous_skills: list[str],
    current_text: str,
) -> list[str]:
    """
    保持旧接口不变：
    优先走 LLM 技能更新，失败时回退到规则版。
    """
    try:
        result = extract_skill_updates_by_llm(previous_skills, current_text)
        return result.get("current_skills", sorted(list(set(previous_skills or []))))
    except Exception:
        result = extract_skill_updates_rule_based(previous_skills, current_text)
        return result.get("current_skills", sorted(list(set(previous_skills or []))))


def classify_job_task_core(question: str) -> str:
    """
    规则分类器：作为 LLM 分类失败时的兜底逻辑保留。
    """
    q = _normalize_text(question)

    compare_keywords = [
        "compare", "difference", "vs", "versus",
        "比较", "对比", "区别", "哪个好", "哪个更适合",
    ]
    gap_keywords = [
        "还差", "缺什么", "差距", "不足", "需要补",
        "what skills am i missing", "missing skills", "gap",
    ]
    course_keywords = [
        "课程", "学习", "怎么学", "学什么", "推荐课程",
        "course", "learn", "study", "learning path",
    ]
    recommend_keywords = [
        "适合什么岗位", "适合什么工作", "推荐岗位", "推荐工作", "岗位推荐",
        "what job fits me", "recommended jobs", "suitable jobs", "which job",
    ]
    general_keywords = [
        "岗位方向", "职业方向", "职业发展", "有哪些岗位",
        "career path", "job direction", "career direction",
    ]

    correction_keywords = [
        "我不会", "我没有", "我不懂", "我不熟", "不是我的技能",
        "去掉", "删掉", "删除", "移除", "去除",
        "纠正一下", "你记错了", "你记错", "我说错了",
        "不会sql", "不会 python", "不会 pandas",
    ]

    skill_recall_keywords = [
        "我还有什么技能",
        "我现在会什么",
        "你记得我会什么",
        "我的技能有哪些",
        "what skills do i have",
        "my skills",
    ]

    fallback_keywords = [
        "怎么准备面试",
        "怎么选方向",
        "我适合走哪条路",
        "简历怎么写",
        "怎么规划",
        "你建议我",
        "给我建议",
        "如何准备",
        "怎么学习更好",
        "帮我分析一下",
    ]

    if any(keyword in q for keyword in correction_keywords):
        return "memory_update"

    if any(keyword in q for keyword in skill_recall_keywords):
        return "memory_update"

    if any(keyword in q for keyword in compare_keywords):
        return "compare_job"
    if any(keyword in q for keyword in gap_keywords):
        return "analyze_gap"
    if any(keyword in q for keyword in course_keywords):
        return "recommend_course"
    if any(keyword in q for keyword in recommend_keywords):
        return "recommend_job"
    if any(keyword in q for keyword in general_keywords):
        return "general_career_question"

    if any(keyword in q for keyword in fallback_keywords):
        return "fallback_llm"

    job_hint_keywords = ["岗位", "工作", "职位", "job", "career"]
    if any(keyword in q for keyword in job_hint_keywords):
        return "recommend_job"

    return "fallback_llm"


def plan_task_core(task_type: str) -> list[str]:
    mapping = {
        "recommend_job": ["recommend", "course", "summarize"],
        "analyze_gap": ["gap", "course", "summarize"],
        "recommend_course": ["course", "summarize"],
        "compare_job": ["compare", "summarize"],
        "general_career_question": ["recommend", "summarize"],
        "memory_update": ["memory_update", "summarize"],
        "fallback_llm": ["fallback_llm"],
    }
    return mapping.get(task_type, ["fallback_llm"])


def recommend_jobs_core(skills_text: str) -> dict[str, Any]:
    user_skills = _normalize_and_filter_skills(
        [s.strip() for s in skills_text.split("、") if s.strip()]
    )
    if not user_skills:
        return {
            "input_skills": [],
            "recommended_jobs": [],
            "job_match_scores": {},
            "matched_skills": {},
            "missing_skills": {},
        }

    jobs = graph_service.get_jobs_with_required_skills()
    if not jobs:
        return {
            "input_skills": user_skills,
            "recommended_jobs": [],
            "job_match_scores": {},
            "matched_skills": {},
            "missing_skills": {},
        }

    ranked = []
    for job in jobs:
        required_skills = job["required_skills"]
        score, matched, missing = _calculate_job_match_score(user_skills, required_skills)
        if score > 0:
            ranked.append({
                "job_name": job["job_name"],
                "score": score,
                "matched_skills": matched,
                "missing_skills": missing,
            })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    top = ranked[:3]

    return {
        "input_skills": user_skills,
        "recommended_jobs": [x["job_name"] for x in top],
        "job_match_scores": {x["job_name"]: x["score"] for x in top},
        "matched_skills": {x["job_name"]: x["matched_skills"] for x in top},
        "missing_skills": {x["job_name"]: x["missing_skills"] for x in top},
    }


def analyze_skill_gap_core(job_name: str, skills_text: str) -> dict[str, Any]:
    user_skills = _normalize_and_filter_skills(
        [s.strip() for s in skills_text.split("、") if s.strip()]
    )
    job = graph_service.get_job_by_name(job_name)
    if job is None:
        return {
            "job_name": job_name,
            "matched_skills": [],
            "missing_skills": [],
        }

    required_skills = graph_service.get_job_required_skills(job_name)
    matched = [skill for skill in required_skills if skill in user_skills]
    missing = [skill for skill in required_skills if skill not in user_skills]

    return {
        "job_name": job_name,
        "matched_skills": matched,
        "missing_skills": missing,
    }


def recommend_courses_core(skills_text: str) -> dict[str, list[str]]:
    target_skills = _normalize_and_filter_skills(
        [s.strip() for s in skills_text.split("、") if s.strip()]
    )
    if not target_skills:
        return {}

    courses = graph_service.get_courses_for_skills(target_skills)
    result: dict[str, list[str]] = {skill: [] for skill in target_skills}

    for item in courses:
        for skill in item["covered_skills"]:
            if skill in result and item["course_name"] not in result[skill]:
                result[skill].append(item["course_name"])

    return result


def compare_jobs_core(job_a: str, job_b: str, skills_text: str = "") -> dict[str, Any]:
    job_a = job_a.strip() if job_a else ""
    job_b = job_b.strip() if job_b else ""

    if not job_a or not job_b:
        return {
            "comparison": "未识别到两个有效岗位，暂时无法完成对比。",
            "fit": {},
        }

    info_a = graph_service.get_job_by_name(job_a)
    info_b = graph_service.get_job_by_name(job_b)

    if info_a is None or info_b is None:
        return {
            "comparison": f"岗位 {job_a} 或 {job_b} 不存在于知识图谱中。",
            "fit": {},
        }

    skills_a = graph_service.get_job_required_skills(job_a)
    skills_b = graph_service.get_job_required_skills(job_b)

    shared = sorted(list(set(skills_a) & set(skills_b)))
    only_a = sorted(list(set(skills_a) - set(skills_b)))
    only_b = sorted(list(set(skills_b) - set(skills_a)))

    user_skills = _normalize_and_filter_skills(
        [s.strip() for s in skills_text.split("、") if s.strip()]
    ) if skills_text else []

    fit = {}
    if user_skills:
        score_a, matched_a, missing_a = _calculate_job_match_score(user_skills, skills_a)
        score_b, matched_b, missing_b = _calculate_job_match_score(user_skills, skills_b)
        fit = {
            job_a: {"score": score_a, "matched": matched_a, "missing": missing_a},
            job_b: {"score": score_b, "matched": matched_b, "missing": missing_b},
        }

    comparison_text = (
        f"{job_a} 与 {job_b} 的共同技能：{', '.join(shared) if shared else '无'}。\n"
        f"{job_a} 特有技能：{', '.join(only_a) if only_a else '无'}。\n"
        f"{job_b} 特有技能：{', '.join(only_b) if only_b else '无'}。"
    )

    return {
        "comparison": comparison_text,
        "fit": fit,
    }


def build_memory_update_result(
    previous_skills: list[str],
    current_text: str,
) -> dict[str, Any]:
    try:
        return extract_skill_updates_by_llm(previous_skills, current_text)
    except Exception:
        return extract_skill_updates_rule_based(previous_skills, current_text)


@tool
def classify_job_task(question: str) -> str:
    """Classify a job-related question."""
    return classify_job_task_core(question)


@tool
def recommend_jobs_by_skills(skills_text: str) -> str:
    """Recommend jobs using the knowledge graph."""
    return json.dumps(recommend_jobs_core(skills_text), ensure_ascii=False)


@tool
def analyze_skill_gap_for_job(job_name: str, skills_text: str) -> str:
    """Analyze the skill gap between a job and the user's current skills."""
    return json.dumps(analyze_skill_gap_core(job_name, skills_text), ensure_ascii=False)


@tool
def recommend_courses_for_missing_skills(skills_text: str) -> str:
    """Recommend courses for missing skills using the knowledge graph."""
    return json.dumps(recommend_courses_core(skills_text), ensure_ascii=False)


@tool
def compare_jobs(job_a: str, job_b: str, skills_text: str = "") -> str:
    """Compare two jobs using the knowledge graph."""
    return json.dumps(compare_jobs_core(job_a, job_b, skills_text), ensure_ascii=False)