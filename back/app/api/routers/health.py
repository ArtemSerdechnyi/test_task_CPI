from fastapi import APIRouter
from fastapi import status

health_router = APIRouter()


@health_router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
    }
