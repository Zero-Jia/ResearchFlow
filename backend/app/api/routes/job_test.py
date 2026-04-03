from fastapi import APIRouter
from app.schemas.job_api import JobTestResponse

router = APIRouter(prefix="/job-test",tags=["job-test"])

@router.get("/",response_model=JobTestResponse)
def test_job_route():
    return JobTestResponse(message="JobKG-Agent route is ready")