from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.point import Point
from app.schemas.point import PointCreate, PointUpdate
from uuid import UUID
from geojson import Point as GeoJSONPoint, loads
import json
from app.middleware.logger import logger

# Common messages and logger context
invalid_point = "Invalid GeoJSON Point"
logger_point = "app.services.v1.point_service"

# Custom exception for missing resources
class NotFoundError(Exception):
    """Custom exception for not found resources.""" 
    pass

# Serialize point to include latitude and longitude
def serialize_point(point):
    return {
        "name": point.name,
        "geom": {
            "latitude": point.geom["coordinates"][0],
            "longitude": point.geom["coordinates"][1]
        },
        "description": point.description,
        "status": point.status,
        "id": str(point.id),
        "created_at": point.created_at,
        "updated_at": point.updated_at
    }

# Create a new point record in the database
async def create_point(db: AsyncSession, point: PointCreate):
    # Validate that the geometry is a valid GeoJSON Point
    try:
        geom_json = json.dumps(point.geom)
        geom_obj = loads(geom_json)
        if not isinstance(geom_obj, GeoJSONPoint):
            raise ValueError(invalid_point)
    except ValueError as e:
        logger.error(invalid_point, error_message=str(e), logger=logger_point)
        raise

    # Create and persist the point
    db_point = Point(
        name=point.name,
        geom=point.geom,
        description=point.description,
        status=point.status,
    )
    db.add(db_point)
    await db.commit()
    await db.refresh(db_point)
    logger.info("Point created", point_id=str(db_point.id), name=point.name, logger=logger_point)
    return db_point

# Fetch a single point by its ID
async def get_point(db: AsyncSession, point_id: UUID):
    result = await db.execute(select(Point).filter(Point.id == point_id))
    point = result.scalars().first()
    if point is None:
        logger.warning("Point not found", point_id=str(point_id), logger=logger_point)
        raise NotFoundError(f"Point with ID {point_id} not found")
    return serialize_point(point)

# Retrieve all points from the database
async def get_all_points(db: AsyncSession):
    result = await db.execute(select(Point))
    points = result.scalars().all()
    logger.info("Fetched all points", count=len(points), logger=logger_point)
    return [serialize_point(point) for point in points]

# Update an existing point by ID
async def update_point(db: AsyncSession, point_id: UUID, point_update: PointUpdate):
    result = await db.execute(select(Point).filter(Point.id == point_id))
    db_point = result.scalars().first()
    if not db_point:
        logger.warning("Point not found for update", point_id=str(point_id), logger=logger_point)
        raise NotFoundError(f"Point with ID {point_id} not found")

    # Validate updated geometry if present
    if point_update.geom:
        try:
            geom_json = json.dumps(point_update.geom)
            geom_obj = loads(geom_json)
            if not isinstance(geom_obj, GeoJSONPoint):
                raise ValueError(invalid_point)
        except ValueError as e:
            logger.error("Invalid GeoJSON Point for update", error_message=str(e), logger=logger_point)
            raise

    # Apply updates only to provided fields
    update_data = point_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key not in ["created_at", "updated_at"]:
            setattr(db_point, key, value)

    await db.commit()
    await db.refresh(db_point)
    logger.info("Point updated", point_id=str(point_id), name=db_point.name, logger=logger_point)
    return serialize_point(db_point)

# Delete a point by its ID
async def delete_point(db: AsyncSession, point_id: UUID):
    result = await db.execute(select(Point).filter(Point.id == point_id))
    db_point = result.scalars().first()
    if not db_point:
        logger.warning("Point not found for deletion", point_id=str(point_id), logger=logger_point)
        raise NotFoundError(f"Point with ID {point_id} not found")
    await db.delete(db_point)
    await db.commit()
    logger.info("Point deleted", point_id=str(point_id), logger=logger_point)
    return None  # Deletion successful
