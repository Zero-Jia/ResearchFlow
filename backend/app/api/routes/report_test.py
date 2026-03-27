from fastapi import APIRouter, HTTPException

from app.agent.structured_agent import structured_researchflow_agent
from app.schemas.report_api import ReportTestRequest, ReportTestResponse

router = APIRouter()


@router.post("/report-test", response_model=ReportTestResponse)
def report_test(request: ReportTestRequest):
    try:
        report = structured_researchflow_agent.run(request.question)
        return ReportTestResponse(
            question=request.question,
            report=report,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Structured report generation failed: {str(e)}"
        )