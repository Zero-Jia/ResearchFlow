from typing import List
from pydantic import BaseModel, Field


class GraphSkillItem(BaseModel):
    name: str = Field(..., description="技能名称")
    courses: List[str] = Field(default_factory=list, description="覆盖该技能的课程")


class GraphJobViewResponse(BaseModel):
    job_name: str
    category: str
    description: str
    skills: List[GraphSkillItem] = Field(default_factory=list)