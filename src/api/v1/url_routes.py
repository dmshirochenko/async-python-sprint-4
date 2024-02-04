from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/health")
async def read_root():
    return "Welcome to the URL shortener API :)"

