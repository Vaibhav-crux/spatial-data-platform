from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class PolygonBase(BaseModel):
    # Base schema for Polygon, includes common fields used in creation and update
    name: str  # Name of the polygon (e.g., "Polygon A")
    geom: Dict[str, Any]  # GeoJSON representation of the polygon as a dictionary
    description: Optional[str] = None  # Optional description for the polygon
    status: str = "active"  # Status of the polygon, default is "active"

class PolygonCreate(PolygonBase):
    # Schema for creating a new polygon, inherits from PolygonBase
    pass

class PolygonUpdate(PolygonBase):
    # Schema for updating an existing polygon, fields are optional
    name: Optional[str] = None  # Optional name update
    geom: Optional[Dict[str, Any]] = None  # Optional geometry update
    status: Optional[str] = None  # Optional status update

class PolygonResponse(PolygonBase):
    # Schema for the response when fetching polygon data, includes ID and timestamps
    id: UUID  # Unique identifier for the polygon
    created_at: datetime  # Timestamp when the polygon was created
    updated_at: datetime  # Timestamp when the polygon was last updated
    
    class Config:
        # Pydantic configuration for custom serialization
        from_attributes = True  # Enable automatic population of attributes
        json_encoders = {UUID: str}  # Convert UUIDs to strings for JSON serialization
