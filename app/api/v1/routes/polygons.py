from fastapi import APIRouter, Depends
from app.services.v1.polygon_service import (
    create_polygon, get_polygon, get_all_polygons,
    update_polygon, delete_polygon, NotFoundError
)
from app.schemas.polygon import PolygonCreate, PolygonResponse, PolygonUpdate
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db

router = APIRouter()
POLYGON_NOT_FOUND = "Polygon not found"

# Endpoint to create a new polygon
@router.post("/", response_model=PolygonResponse, status_code=201)
async def create_polygon_endpoint(polygon: PolygonCreate, db: AsyncSession = Depends(get_db)):
    return await create_polygon(db, polygon)

# Endpoint to retrieve a polygon by its ID
@router.get("/{polygon_id}", response_model=PolygonResponse)
async def get_polygon_endpoint(polygon_id: UUID, db: AsyncSession = Depends(get_db)):
    polygon = await get_polygon(db, polygon_id)
    if polygon is None:
        raise NotFoundError(POLYGON_NOT_FOUND)
    return polygon

# Endpoint to retrieve all polygons
@router.get("/", response_model=list[PolygonResponse])
async def get_all_polygons_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_all_polygons(db)

# Endpoint to fully update a polygon by its ID
@router.put("/{polygon_id}", response_model=PolygonResponse)
async def update_polygon_endpoint(polygon_id: UUID, polygon: PolygonUpdate, db: AsyncSession = Depends(get_db)):
    polygon_updated = await update_polygon(db, polygon_id, polygon)
    if polygon_updated is None:
        raise NotFoundError(POLYGON_NOT_FOUND)
    return polygon_updated

# Endpoint to partially update a polygon by its ID
@router.patch("/{polygon_id}", response_model=PolygonResponse)
async def patch_polygon_endpoint(polygon_id: UUID, polygon: PolygonUpdate, db: AsyncSession = Depends(get_db)):
    polygon_updated = await update_polygon(db, polygon_id, polygon)
    if polygon_updated is None:
        raise NotFoundError(POLYGON_NOT_FOUND)
    return polygon_updated

# Endpoint to delete a polygon by its ID
@router.delete("/{polygon_id}")
async def delete_polygon_endpoint(polygon_id: UUID, db: AsyncSession = Depends(get_db)):
    await delete_polygon(db, polygon_id)
    return {"message": "Polygon deleted successfully"}