from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config.settings import settings
from app.models.point import Point
from app.models.polygon import Polygon, Base
from app.middleware.logger import logger  # <-- use structured logger
import ssl
import os

# Validate CA certificate file existence
ca_cert_path = os.path.join(os.path.dirname(__file__), '..', '..', settings.CA_CERT_PATH)
ca_cert_path = os.path.abspath(ca_cert_path)
if not os.path.exists(ca_cert_path):
    raise FileNotFoundError(f"CA certificate file not found at: {ca_cert_path}")

# Configure SSL context with the Aiven CA certificate
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.load_verify_locations(ca_cert_path)

# Create SQLAlchemy async engine
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USERNAME_TEST}:{settings.DB_PASSWORD_TEST}"
    f"@{settings.DB_HOST_TEST}:{settings.DB_PORT_TEST}/{settings.DB_DATABASE_TEST}"
)
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": ssl_context},
    echo=False
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    try:
        async with engine.connect() as conn:
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

            # Verify table existence
            result = await conn.execute(text('''
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('points', 'polygons');
            '''))
            tables = [row[0] for row in result.fetchall()]
            if 'points' not in tables:
                logger.error("Points table was not created")
                raise RuntimeError("Points table was not created")
            if 'polygons' not in tables:
                logger.error("Polygons table was not created")
                raise RuntimeError("Polygons table was not created")
            
            # Log only the required messages
            logger.info("Database connection established")
            logger.info(f"Tables: {tables}")

            # Create PostGIS and UUID extensions
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS postgis;'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            await conn.commit()

            # Add computed geometry columns
            await conn.execute(text('''
                ALTER TABLE points
                ADD COLUMN IF NOT EXISTS geom_postgis GEOMETRY(POINT, 4326)
                GENERATED ALWAYS AS (ST_GeomFromGeoJSON(geom)) STORED;
            '''))
            await conn.execute(text('''
                ALTER TABLE polygons
                ADD COLUMN IF NOT EXISTS geom_postgis GEOMETRY(POLYGON, 4326)
                GENERATED ALWAYS AS (ST_GeomFromGeoJSON(geom)) STORED;
            '''))
            await conn.commit()

            # Create indexes
            await conn.execute(text('CREATE INDEX IF NOT EXISTS points_name_idx ON points (name);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS points_created_at_idx ON points (created_at);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS points_updated_at_idx ON points (updated_at);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS points_geom_idx ON points USING GIST (geom_postgis);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS polygons_name_idx ON polygons (name);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS polygons_created_at_idx ON polygons (created_at);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS polygons_updated_at_idx ON polygons (updated_at);'))
            await conn.execute(text('CREATE INDEX IF NOT EXISTS polygons_geom_idx ON polygons USING GIST (geom_postgis);'))
            await conn.commit()

    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

async def check_db_health():
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text('''
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('points', 'polygons');
            '''))
            tables = [row[0] for row in result.fetchall()]
            return {
                "connection": "successful",
                "tables": {
                    "points": "points" in tables,
                    "polygons": "polygons" in tables
                }
            }
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "connection": "failed",
            "error": str(e),
            "tables": {
                "points": False,
                "polygons": False
            }
        }

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session