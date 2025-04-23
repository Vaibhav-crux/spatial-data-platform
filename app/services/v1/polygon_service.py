from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.polygon import Polygon
from app.schemas.polygon import PolygonCreate, PolygonUpdate
from uuid import UUID
from geojson import Polygon as GeoJSONPolygon, loads
import json
from app.middleware.logger import logger

# Custom error message for invalid polygons
invalid_polygon = "Invalid GeoJSON Polygon"

# Custom exception for resources not found
class NotFoundError(Exception):
    """Custom exception for not found resources.""" 
    pass

# Serialize polygon to include latitude and longitude
def serialize_polygon(polygon):
    # Convert GeoJSON Polygon coordinates to latitude/longitude pairs
    lat_lon_coords = [
        [{"latitude": coord[1], "longitude": coord[0]} for coord in ring]
        for ring in polygon.geom["coordinates"]
    ]
    return {
        "name": polygon.name,
        "geom": {
            "type": "Polygon",
            "coordinates": lat_lon_coords
        },
        "description": polygon.description,
        "status": polygon.status,
        "id": str(polygon.id),
        "created_at": polygon.created_at,
        "updated_at": polygon.updated_at
    }

# Create a new polygon entry in the database
async def create_polygon(db: AsyncSession, polygon: PolygonCreate):
    # Validate that the input geometry is a proper GeoJSON Polygon
    try:
        geom_json = json.dumps(polygon.geom)
        geom_obj = loads(geom_json)
        if not isinstance(geom_obj, GeoJSONPolygon):
            raise ValueError(invalid_polygon)
    except ValueError as e:
        logger.error(invalid_polygon, error_message=str(e))
        raise

    # Create and persist the polygon
    db_polygon = Polygon(
        name=polygon.name,
        geom=polygon.geom,
        description=polygon.description,
        status=polygon.status,
    )
    db.add(db_polygon)
    await db.commit()
    await db.refresh(db_polygon)
    logger.info("Polygon created", polygon_id=str(db_polygon.id), name=polygon.name)
    return db_polygon

# Retrieve a polygon by its unique ID
async def get_polygon(db: AsyncSession, polygon_id: UUID):
    result = await db.execute(select(Polygon).filter(Polygon.id == polygon_id))
    polygon = result.scalars().first()
    if polygon is None:
        logger.warning("Polygon not found", polygon_id=str(polygon_id))
        raise NotFoundError(f"Polygon with ID {polygon_id} not found")
    return serialize_polygon(polygon)

# Retrieve all polygons from the database
async def get_all_polygons(db: AsyncSession):
    result = await db.execute(select(Polygon))
    polygons = result.scalars().all()
    serialized_polygons = [serialize_polygon(polygon) for polygon in polygons]
    logger.info("Fetched all polygons", count=len(polygons))
    return serialized_polygons

# Update an existing polygon
async def update_polygon(db: AsyncSession, polygon_id: UUID, polygon_update: PolygonUpdate):
    result = await db.execute(select(Polygon).filter(Polygon.id == polygon_id))
    db_polygon = result.scalars().first()
    if not db_polygon:
        logger.warning("Polygon not found for update", polygon_id=str(polygon_id))
        raise NotFoundError(f"Polygon with ID {polygon_id} not found")

    # Validate new geometry if provided
    if polygon_update.geom:
        try:
            geom_json = json.dumps(polygon_update.geom)
            geom_obj = loads(geom_json)
            if not isinstance(geom_obj, GeoJSONPolygon):
                raise ValueError(invalid_polygon)
        except ValueError as e:
            logger.error("Invalid GeoJSON Polygon for update", error_message=str(e))
            raise

    # Update only the provided fields
    update_data = polygon_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key not in ["created_at", "updated_at"]:
            setattr(db_polygon, key, value)

    await db.commit()
    await db.refresh(db_polygon)
    logger.info("Polygon updated", polygon_id=str(polygon_id), name=db_polygon.name)
    return serialize_polygon(db_polygon)

# Delete a polygon by its ID
async def delete_polygon(db: AsyncSession, polygon_id: UUID):
    result = await db.execute(select(Polygon).filter(Polygon.id == polygon_id))
    db_polygon = result.scalars().first()
    if not db_polygon:
        logger.warning("Polygon not found for deletion", polygon_id=str(polygon_id))
        raise NotFoundError(f"Polygon with ID {polygon_id} not found")
    await db.delete(db_polygon)
    await db.commit()
    logger.info("Polygon deleted", polygon_id=str(polygon_id))
    return None # Deletion successful
