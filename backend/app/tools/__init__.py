from app.tools.simple_tools import get_current_project_name,explain_agent_role
from app.tools.research_tools import (
    search_research_knowledge,
    summarize_research_content,
)

TOOLS = [
    get_current_project_name,
    explain_agent_role,
    search_research_knowledge,
    summarize_research_content,
]