from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.db_test import router as db_test_router
from app.api.routes.llm_test import router as llm_test_router
from app.api.routes.agent_test import router as agent_test_router
from app.api.routes.research_test import router as research_test_router

api_router = APIRouter()

api_router.include_router(health_router,tags=["Health"])
api_router.include_router(db_test_router, tags=["Database"])
api_router.include_router(llm_test_router, tags=["LLM"])
api_router.include_router(agent_test_router, tags=["Agent"])
api_router.include_router(research_test_router,tags=["Research"])