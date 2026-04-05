from fastapi import APIRouter, HTTPException

from app.schemas.job_recommendation_api import (
    JobRecommendationRequest,
    JobRecommendationResponse,
)
from app.services.job_service import job_service

router = APIRouter()


@router.post("/job/recommend", response_model=JobRecommendationResponse)
def recommend_job(request: JobRecommendationRequest):
    try:
        if not request.question.strip() and not request.skills:
            raise HTTPException(status_code=400, detail="问题和技能不能同时为空")

        normalized_skills, report = job_service.run_memory_chat(
            question=request.question,
            skills=request.skills,
            session_id=request.session_id if request.session_id is not None else 0,
            user_id=request.user_id,
        )

        if not report.input_skills:
            report.input_skills = normalized_skills

        return JobRecommendationResponse(
            normalized_skills=normalized_skills,
            report=report,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job recommendation failed: {str(e)}")