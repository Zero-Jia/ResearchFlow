from langchain.tools import tool

from app.data.job_kg_mock import SKILL_ALIASES
from app.services.graph_service import graph_service


def _normalize_skill(skill: str) -> str:
    skill_lower = skill.strip().lower()
    return SKILL_ALIASES.get(skill_lower, skill.strip())


def _extract_skills_from_text(text: str) -> list[str]:
    text_lower = text.lower()
    found_skills = []

    for alias, normalized in SKILL_ALIASES.items():
        if alias.lower() in text_lower and normalized not in found_skills:
            found_skills.append(normalized)

    return found_skills


@tool
def classify_job_task(question: str) -> str:
    """
    Classify the user's job-related question into one of these task types:
    recommend_job, analyze_gap, recommend_course, compare_job, or general_career_question.

    Use this tool before deciding how to answer a career-related request.
    """
    q = question.lower()

    compare_keywords = [
        "compare", "difference", "vs", "versus",
        "比较", "对比", "区别", "哪个好", "哪个更适合"
    ]

    gap_keywords = [
        "还差", "缺什么", "差距", "不足", "需要补",
        "what skills am i missing", "missing skills", "gap"
    ]

    course_keywords = [
        "课程", "学习", "怎么学", "学什么", "推荐课程",
        "course", "learn", "study", "learning path"
    ]

    recommend_keywords = [
        "适合什么岗位", "适合什么工作", "推荐岗位", "推荐工作", "岗位推荐",
        "what job fits me", "recommended jobs", "suitable jobs", "which job"
    ]

    general_keywords = [
        "岗位方向", "职业方向", "职业发展", "有哪些岗位",
        "career path", "job direction", "career direction"
    ]

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

    job_hint_keywords = ["岗位", "工作", "职位", "job", "career"]

    if any(keyword in q for keyword in job_hint_keywords):
        return "recommend_job"

    return "general_career_question"


@tool
def recommend_jobs_by_skills(skills_text: str) -> str:
    """
    Recommend jobs based on the user's current skills using the job knowledge graph.
    Input can be a natural language sentence or a skill list.
    Returns ranked jobs with match scores, matched skills, and missing skills.
    """
    user_skills = _extract_skills_from_text(skills_text)

    if not user_skills:
        return "No recognizable skills were found in the user's input."

    jobs = graph_service.get_jobs_with_required_skills()
    if not jobs:
        return "No job data was found in the knowledge graph."

    results = []

    for job in jobs:
        required_skills = job["required_skills"]
        matched = [skill for skill in required_skills if skill in user_skills]
        missing = [skill for skill in required_skills if skill not in user_skills]

        score = round(len(matched) / len(required_skills), 2) if required_skills else 0.0

        if score > 0:
            results.append({
                "job_name": job["job_name"],
                "score": score,
                "matched_skills": matched,
                "missing_skills": missing,
            })

    if not results:
        return "No suitable jobs were found based on the current skills."

    results.sort(key=lambda x: x["score"], reverse=True)
    top_results = results[:3]

    lines = []
    for idx, item in enumerate(top_results, start=1):
        lines.append(
            f"{idx}. Job: {item['job_name']}\n"
            f"   Score: {item['score']}\n"
            f"   Matched Skills: {', '.join(item['matched_skills']) if item['matched_skills'] else 'None'}\n"
            f"   Missing Skills: {', '.join(item['missing_skills']) if item['missing_skills'] else 'None'}"
        )

    return "\n\n".join(lines)


@tool
def analyze_skill_gap_for_job(job_name: str, skills_text: str) -> str:
    """
    Analyze the gap between a target job and the user's current skills using the knowledge graph.
    Returns matched skills and missing skills for the target job.
    """
    user_skills = _extract_skills_from_text(skills_text)

    job = graph_service.get_job_by_name(job_name)
    if job is None:
        return f"Job '{job_name}' was not found in the knowledge graph."

    required_skills = graph_service.get_job_required_skills(job_name)
    matched = [skill for skill in required_skills if skill in user_skills]
    missing = [skill for skill in required_skills if skill not in user_skills]

    return (
        f"Job: {job_name}\n"
        f"Matched Skills: {', '.join(matched) if matched else 'None'}\n"
        f"Missing Skills: {', '.join(missing) if missing else 'None'}"
    )


@tool
def recommend_courses_for_missing_skills(skills_text: str) -> str:
    """
    Recommend courses for the skills the user wants to improve using the knowledge graph.
    Input can be missing skills or a natural language request mentioning target skills.
    """
    target_skills = _extract_skills_from_text(skills_text)

    if not target_skills:
        return "No recognizable target skills were found for course recommendation."

    courses = graph_service.get_courses_for_skills(target_skills)
    if not courses:
        return "No suitable courses were found for the given skills."

    lines = []
    for idx, item in enumerate(courses, start=1):
        lines.append(
            f"{idx}. Course: {item['course_name']}\n"
            f"   Platform: {item['platform']}\n"
            f"   Covered Skills: {', '.join(item['covered_skills'])}"
        )

    return "\n\n".join(lines)