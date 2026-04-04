from typing import List
from pydantic import BaseModel, Field

class JobCard(BaseModel):
    job_name: str = Field(..., description="岗位名称")
    score: float = Field(..., description="匹配分数")
    matched_skills: List[str] = Field(default_factory=list, description="已匹配技能")
    missing_skills: List[str] = Field(default_factory=list, description="缺失技能")
    recommended_courses: List[str] = Field(default_factory=list, description="推荐课程")

class JobRecommendationViewResponse(BaseModel):
    task_id: int
    question: str
    normalized_skills: List[str] = Field(default_factory=list, description="标准化后的用户技能")
    task_type: str
    job_cards: List[JobCard] = Field(default_factory=list, description="推荐岗位卡片列表")
    comparison: str | None = Field(default=None, description="岗位对比结果")
    suggestions: List[str] = Field(default_factory=list, description="总体建议")