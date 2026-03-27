from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.llm import LLMTestRequest, LLMTestResponse
from app.services.llm_service import llm_service

router = APIRouter()


@router.post("/llm-test", response_model=LLMTestResponse)
def llm_test(request: LLMTestRequest):
    if not settings.LLM_API_KEY:
        raise HTTPException(status_code=500, detail="Missing API key")

    try:
        ai_message = llm_service.chat(request.message)

        return LLMTestResponse(
            user_message=request.message,
            ai_message=ai_message,
            model=settings.LLM_MODEL
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))