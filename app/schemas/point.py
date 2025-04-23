from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class PointBase(BaseModel):
    # Base schema for Point, includes common fields used in creation and update
    name: str  # Name of the point (e.g., "Point A")
    geom: Dict[str, Any]  # GeoJSON representation of the point as a dictionary
    description: Optional[str] = None  # Optional description for the point
    status: str = "active"  # Status of the point, default is "active"

class PointCreate(PointBase):
    # Schema for creating a new point, inherits from PointBase
    pass

class PointUpdate(PointBase):
    # Schema for updating an existing point, fields are optional
    name: Optional[str] = None  # Optional name update
    geom: Optional[Dict[str, Any]] = None  # Optional geometry update
    status: Optional[str] = None  # Optional status update

class PointResponse(PointBase):
    # Schema for the response when fetching point data, includes ID and timestamps
    id: UUID  # Unique identifier for the point
    created_at: datetime  # Timestamp when the point was created
    updated_at: datetime  # Timestamp when the point was last updated
    
    class Config:
        # Pydantic configuration for custom serialization
        from_attributes = True  # Enable automatic population of attributes
        json_encoders = {UUID: str}  # Convert UUIDs to strings for JSON serialization
