from fastapi import APIRouter, HTTPException

from app.schemas.job_chat_api import JobChatRequest, JobChatResponse
from app.services.job_service import job_service

router = APIRouter()


@router.post("/job/chat", response_model=JobChatResponse)
def job_chat(request: JobChatRequest):
    try:
        normalized_skills, report = job_service.run_memory_chat(
            question=request.question,
            skills=request.skills,
            session_id=request.session_id,
            user_id=request.user_id,
        )

        return JobChatResponse(
            session_id=request.session_id,
            normalized_skills=normalized_skills,
            report=report,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job chat failed: {str(e)}")