from sqlalchemy import Column, String, JSON, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.point import Base
from sqlalchemy.sql import func
import uuid

class Polygon(Base):
    __tablename__ = "polygons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    geom = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Polygon(name={self.name})>"
