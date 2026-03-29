from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.research_task_api import (
    CreateResearchTaskRequest,
    CreateResearchTaskResponse,
    ResearchTaskDetailResponse,
    ResearchTaskHistoryResponse,
    ResearchTaskSummaryItem,
    ReportData,
)
from app.services.research_service import research_service

router = APIRouter()


@router.post("/research/create", response_model=CreateResearchTaskResponse)
def create_research_task(request: CreateResearchTaskRequest, db: Session = Depends(get_db)):
    try:
        task, report = research_service.create_task_and_generate_report(
            db=db,
            user_id=request.user_id,
            session_id=request.session_id,
            question=request.question,
        )

        parsed_report = research_service.parse_report(report)
        return CreateResearchTaskResponse(
            task_id=task.id,
            task_type=task.task_type,
            topic=task.topic,
            status=task.status,
            report=ReportData(**parsed_report),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Create research task failed: {str(e)}")


@router.get("/research/detail/{task_id}", response_model=ResearchTaskDetailResponse)
def get_research_task_detail(task_id: int, db: Session = Depends(get_db)):
    task, report = research_service.get_task_detail(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    parsed_report = research_service.parse_report(report)

    return ResearchTaskDetailResponse(
        task_id=task.id,
        user_id=task.user_id,
        session_id=task.session_id,
        task_type=task.task_type,
        topic=task.topic,
        user_input=task.user_input,
        status=task.status,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        report=ReportData(**parsed_report) if parsed_report else None,
    )


@router.get("/research/history/{user_id}", response_model=ResearchTaskHistoryResponse)
def get_research_task_history(user_id: int, db: Session = Depends(get_db)):
    tasks = research_service.list_tasks_by_user(db, user_id)

    items = [
        ResearchTaskSummaryItem(
            task_id=task.id,
            task_type=task.task_type,
            topic=task.topic,
            status=task.status,
            created_at=task.created_at.isoformat(),
        )
        for task in tasks
    ]

    return ResearchTaskHistoryResponse(items=items)