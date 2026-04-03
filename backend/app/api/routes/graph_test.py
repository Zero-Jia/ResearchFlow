from fastapi import APIRouter, HTTPException

from app.services.graph_service import graph_service

router = APIRouter()


@router.get("/graph-test")
def graph_test():
    try:
        result = graph_service.test_connection()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Graph connection failed: {str(e)}"
        )