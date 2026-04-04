from app.tools.simple_tools import get_current_project_name,explain_agent_role
from app.tools.research_tools import (
    search_research_knowledge,
    summarize_research_content,
    classify_research_task,
    compare_research_topics,
)

from app.tools.job_tools import (
    classify_job_task,
    recommend_jobs_by_skills,
    analyze_skill_gap_for_job,
    recommend_courses_for_missing_skills,
    compare_jobs
)

RESEARCH_TOOLS = [
    get_current_project_name,
    explain_agent_role,
    search_research_knowledge,
    summarize_research_content,
    classify_research_task,
    compare_research_topics,
]

JOB_TOOLS = [
    get_current_project_name,
    explain_agent_role,
    classify_job_task,
    recommend_jobs_by_skills,
    analyze_skill_gap_for_job,
    recommend_courses_for_missing_skills,
    compare_jobs,
]