from fastapi import APIRouter,HTTPException

from app.agent.core_agent import researchflow_agent
from app.schemas.research import ResearchTestRequest,ResearchTestResponse

router = APIRouter()

@router.post("/research-test",response_model=ResearchTestResponse)
def research_test(request:ResearchTestRequest):
    try:
        answer = researchflow_agent.run(request.question)
        return ResearchTestResponse(
            question=request.question,
            answer=answer,
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Research execution failed: {str(e)}")