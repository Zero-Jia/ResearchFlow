from fastapi import APIRouter, HTTPException

from app.agent.core_agent import researchflow_agent
from app.schemas.agent import AgentTestRequest, AgentTestResponse

router = APIRouter()


@router.post("/agent-test", response_model=AgentTestResponse)
def agent_test(request: AgentTestRequest):
    try:
        result = researchflow_agent.run(request.message)
        return AgentTestResponse(
            user_message=request.message,
            agent_message=result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")