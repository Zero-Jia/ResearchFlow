from fastapi import APIRouter, HTTPException

from app.schemas.graph_view_api import GraphJobViewResponse
from app.services.graph_view_service import graph_view_service

router = APIRouter()


@router.get("/graph/job/{job_name}", response_model=GraphJobViewResponse)
def get_job_graph_view(job_name: str):
    if not job_name.strip():
        raise HTTPException(status_code=400, detail="岗位名称不能为空")

    result = graph_view_service.build_job_graph_view(job_name)
    if result is None:
        raise HTTPException(status_code=404, detail="Job graph view not found")
    return result