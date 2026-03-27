from fastapi import APIRouter, HTTPException

from app.agent.core_agent import researchflow_agent
from app.schemas.compare import CompareTestRequest, CompareTestResponse

router = APIRouter()


@router.post("/compare-test", response_model=CompareTestResponse)
def compare_test(request: CompareTestRequest):
    try:
        answer = researchflow_agent.run(request.question)
        return CompareTestResponse(
            question=request.question,
            answer=answer,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compare execution failed: {str(e)}")