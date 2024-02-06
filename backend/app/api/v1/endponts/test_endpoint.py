from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test():
    return {"message": "Test endpoint is working!"}
