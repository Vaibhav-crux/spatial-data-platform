from fastapi import APIRouter
from app.database.db import check_db_health

router = APIRouter()

@router.get("/")
async def health_check():
    return await check_db_health()