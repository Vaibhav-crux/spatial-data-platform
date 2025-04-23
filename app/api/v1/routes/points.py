from fastapi import APIRouter, Depends
from app.services.v1.point_service import (
    create_point, get_point, get_all_points,
    update_point, delete_point, NotFoundError
)
from app.schemas.point import PointCreate, PointResponse, PointUpdate
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db

router = APIRouter()
POINT_NOT_FOUND = "Point not found"

# Endpoint to create a new point
@router.post("/", response_model=PointResponse, status_code=201)
async def create_point_endpoint(point: PointCreate, db: AsyncSession = Depends(get_db)):
    return await create_point(db, point)

# Endpoint to fetch a single point by ID
@router.get("/{point_id}", response_model=PointResponse)
async def get_point_endpoint(point_id: UUID, db: AsyncSession = Depends(get_db)):
    point = await get_point(db, point_id)
    if point is None:
        raise NotFoundError(POINT_NOT_FOUND)
    return point

# Endpoint to fetch all points
@router.get("/", response_model=list[PointResponse])
async def get_all_points_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_all_points(db)

# Endpoint to fully update a point by ID
@router.put("/{point_id}", response_model=PointResponse)
async def update_point_endpoint(point_id: UUID, point: PointUpdate, db: AsyncSession = Depends(get_db)):
    point_updated = await update_point(db, point_id, point)
    if point_updated is None:
        raise NotFoundError(POINT_NOT_FOUND)
    return point_updated

# Endpoint to partially update a point by ID
@router.patch("/{point_id}", response_model=PointResponse)
async def patch_point_endpoint(point_id: UUID, point: PointUpdate, db: AsyncSession = Depends(get_db)):
    point_updated = await update_point(db, point_id, point)
    if point_updated is None:
        raise NotFoundError(POINT_NOT_FOUND)
    return point_updated

# Endpoint to delete a point by ID
@router.delete("/{point_id}")
async def delete_point_endpoint(point_id: UUID, db: AsyncSession = Depends(get_db)):
    await delete_point(db, point_id)
    return {"message": "Point deleted successfully"}