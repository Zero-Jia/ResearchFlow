from langchain.tools import tool


@tool
def get_current_project_name() -> str:
    """Return the name of the current project."""
    return "ResearchFlow"


@tool
def explain_agent_role() -> str:
    """Explain what this current agent is responsible for."""
    return (
        "This agent is the ResearchFlow assistant. "
        "It helps users handle research-oriented tasks, "
        "decides whether tools are needed, and returns clear answers."
    )


TOOLS = [
    get_current_project_name,
    explain_agent_role,
]