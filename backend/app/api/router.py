from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.db_test import router as db_test_router
from app.api.routes.llm_test import router as llm_test_router
from app.api.routes.agent_test import router as agent_test_router
from app.api.routes.research_test import router as research_test_router
from app.api.routes.compare_test import router as compare_test_router
from app.api.routes.report_test import router as report_test_router
from app.api.routes.research_task import router as research_task_router
from app.api.routes.job_test import router as job_test_router
from app.api.routes.graph_test import router as graph_test_router
from app.api.routes.job_recommendation import router as job_recommendation_router
from app.api.routes.job_task import router as job_task_router
from app.api.routes.job_view import router as job_view_router
from app.api.routes.graph_view import router as graph_view_router
from app.api.routes.job_chat import router as job_chat_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat_ui import router as chat_ui_router
from app.api.routes.chat_stream import router as chat_stream_router
from app.api.routes.chat_reasoning_stream import router as chat_reasoning_stream_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["Health"])
api_router.include_router(db_test_router, tags=["Database"])
api_router.include_router(llm_test_router, tags=["LLM"])
api_router.include_router(agent_test_router, tags=["Agent"])
api_router.include_router(research_test_router, tags=["Research"])
api_router.include_router(compare_test_router, tags=["Compare"])
api_router.include_router(report_test_router, tags=["Report"])
api_router.include_router(research_task_router, tags=["Research Task"])
api_router.include_router(job_test_router, tags=["Job"])
api_router.include_router(graph_test_router, tags=["Graph"])
api_router.include_router(job_recommendation_router, tags=["Job Recommendation"])
api_router.include_router(job_task_router, tags=["Job Task"])
api_router.include_router(job_view_router, tags=["Job View"])
api_router.include_router(graph_view_router, tags=["Graph View"])
api_router.include_router(job_chat_router, tags=["Job Chat"])
api_router.include_router(auth_router, tags=["Auth"])
api_router.include_router(chat_ui_router, tags=["Chat UI"])
api_router.include_router(chat_stream_router, tags=["Chat Stream"])
api_router.include_router(chat_reasoning_stream_router, tags=["Chat Reasoning Stream"])