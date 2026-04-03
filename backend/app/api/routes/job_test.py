from fastapi import APIRouter, HTTPException

from app.agent.job_structured_agent import job_structured_agent
from app.schemas.job_api import JobReportTestRequest, JobReportTestResponse

router = APIRouter()

@router.post("/job_report_test",response_model=JobReportTestResponse)
def job_report_test(request:JobReportTestRequest):
    try:
        report = job_structured_agent.run(request.question)
        return JobReportTestResponse(
            question=request.question,
            report=report,
        )   
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job report generation failed: {str(e)}")