from typing import List, Optional
from pydantic import BaseModel, Field


class ResearchReport(BaseModel):
    """Structured research report returned by the agent."""

    task_type: str = Field(
        ...,
        description="Task type such as research, compare, summary, or general."
    )
    topic: str = Field(
        ...,
        description="Main topic of the user's request."
    )
    summary: str = Field(
        ...,
        description="A concise summary of the final answer."
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Important points extracted from the answer."
    )
    comparison: Optional[str] = Field(
        default=None,
        description="Comparison result if the task is compare-oriented."
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested next steps, study advice, or follow-up actions."
    )