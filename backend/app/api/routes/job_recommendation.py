from fastapi import APIRouter, HTTPException

from app.agent.job_structured_agent import job_structured_agent
from app.schemas.job_recommendation_api import (
    JobRecommendationRequest,
    JobRecommendationResponse,
)
from app.services.user_profile_service import user_profile_service

router = APIRouter()


@router.post("/job/recommend", response_model=JobRecommendationResponse)
def recommend_job(request: JobRecommendationRequest):
    try:
        if not request.question.strip() and not request.skills:
            raise HTTPException(status_code=400, detail="问题和技能不能同时为空")

        merged_skills = user_profile_service.merge_skills(
            explicit_skills=request.skills,
            question=request.question,
        )

        final_prompt = user_profile_service.build_skill_prompt(
            skills=merged_skills,
            question=request.question,
        )

        report = job_structured_agent.run(final_prompt)

        if not report.input_skills:
            report.input_skills = merged_skills

        return JobRecommendationResponse(
            normalized_skills=merged_skills,
            report=report,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job recommendation failed: {str(e)}")