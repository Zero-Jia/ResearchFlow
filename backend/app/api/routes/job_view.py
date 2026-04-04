from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job_view_api import JobRecommendationViewResponse
from app.services.job_service import job_service
from app.services.job_view_service import job_view_service

router = APIRouter()

@router.get("/job/task/view/{task_id}", response_model=JobRecommendationViewResponse)
def get_job_task_view(task_id: int, db: Session = Depends(get_db)):
    task, report = job_service.get_task_detail(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Job task not found")

    rebuilt_report = job_service.rebuild_report_from_db(task, report)
    if rebuilt_report is None:
        raise HTTPException(status_code=404, detail="Job report not found")

    return job_view_service.build_view_response_from_task(
        task=task,
        report_model=rebuilt_report,
    )