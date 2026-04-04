from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job_task_api import (
    CreateJobTaskRequest,
    CreateJobTaskResponse,
    JobTaskHistoryResponse,
    JobTaskSummaryItem,
    JobTaskDetailResponse,
)
from app.services.job_service import job_service

router = APIRouter()


@router.post("/job/task/create", response_model=CreateJobTaskResponse)
def create_job_task(request: CreateJobTaskRequest, db: Session = Depends(get_db)):
    try:
        task, report, normalized_skills, structured_report = job_service.create_job_task_and_report(
            db=db,
            user_id=request.user_id,
            session_id=request.session_id,
            question=request.question,
            skills=request.skills,
        )

        return CreateJobTaskResponse(
            task_id=task.id,
            status=task.status,
            normalized_skills=normalized_skills,
            report=structured_report,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create job task failed: {str(e)}")


@router.get("/job/task/history/{user_id}", response_model=JobTaskHistoryResponse)
def get_job_task_history(user_id: int, db: Session = Depends(get_db)):
    tasks = job_service.list_tasks_by_user(db, user_id)

    items = [
        JobTaskSummaryItem(
            task_id=task.id,
            task_type=task.task_type,
            topic=task.topic,
            status=task.status,
            created_at=task.created_at.isoformat(),
        )
        for task in tasks
    ]

    return JobTaskHistoryResponse(items=items)


@router.get("/job/task/detail/{task_id}", response_model=JobTaskDetailResponse)
def get_job_task_detail(task_id: int, db: Session = Depends(get_db)):
    task, report = job_service.get_task_detail(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Job task not found")

    rebuilt_report = job_service.rebuild_report_from_db(task, report)
    normalized_skills = rebuilt_report.input_skills if rebuilt_report else []

    return JobTaskDetailResponse(
        task_id=task.id,
        user_id=task.user_id,
        session_id=task.session_id,
        task_type=task.task_type,
        topic=task.topic,
        user_input=task.user_input,
        status=task.status,
        normalized_skills=normalized_skills,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        report=rebuilt_report,
    )