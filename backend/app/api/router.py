from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.db_test import router as db_test_router
from app.api.routes.llm_test import router as llm_test_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(db_test_router)
api_router.include_router(llm_test_router)