from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


app = FastAPI(title=settings.PROJECT_NAME)

cors_origins = [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": f"{settings.PROJECT_NAME} backend is ready"
    }

app.include_router(api_router,prefix=settings.API_V1_STR)