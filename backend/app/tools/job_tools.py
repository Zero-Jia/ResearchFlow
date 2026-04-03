from langchain.tools import tool


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

    # 兜底策略：
    # 如果提到了“岗位/工作/job”等词，但没命中特殊意图，默认按 recommend_job 处理
    job_hint_keywords = ["岗位", "工作", "职位", "job", "career"]

    if any(keyword in q for keyword in job_hint_keywords):
        return "recommend_job"

    return "general_career_question"