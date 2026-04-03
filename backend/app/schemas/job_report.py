from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class JobRecommendationReport(BaseModel):
    task_type: str = Field(..., description="Job-related task type")
    input_skills: List[str] = Field(default_factory=list, description="User input skills")
    recommended_jobs: List[str] = Field(default_factory=list, description="Recommended job list")
    job_match_scores: Dict[str, float] = Field(default_factory=dict, description="Job match scores")
    matched_skills: Dict[str, List[str]] = Field(default_factory=dict, description="Matched skills for each job")
    missing_skills: Dict[str, List[str]] = Field(default_factory=dict, description="Missing skills for each job")
    course_recommendations: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Course recommendations for missing skills"
    )
    comparison: Optional[str] = Field(default=None, description="Comparison result if needed")
    suggestions: List[str] = Field(default_factory=list, description="Final suggestions")