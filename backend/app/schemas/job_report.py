from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class JobRecommendationReport(BaseModel):
    """Structured job recommendation report returned by the agent."""

    task_type: str = Field(
        ...,
        description="Task type such as recommend_job, analyze_gap, recommend_course, compare_job, or general_career_question."
    )

    input_skills: List[str] = Field(
        default_factory=list,
        description="Skills extracted or inferred from the user's input."
    )

    recommended_jobs: List[str] = Field(
        default_factory=list,
        description="Top recommended jobs."
    )

    job_match_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Matching score for each recommended job."
    )

    matched_skills: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Matched skills between user and each job."
    )

    missing_skills: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Missing skills for each recommended job."
    )

    course_recommendations: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Recommended courses for missing skills."
    )

    comparison: Optional[str] = Field(
        default=None,
        description="Comparison result when the task is job comparison."
    )

    suggestions: List[str] = Field(
        default_factory=list,
        description="Final suggestions or action recommendations."
    )