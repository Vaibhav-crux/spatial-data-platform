# Spatial Data Platform

This project consists of a **FastAPI** backend designed for handling spatial data. It provides endpoints for handling points and polygons, and includes functionality for API testing and integration with a database. The project is containerized using **Docker** and orchestrated with **Docker Compose**.

## Project Structure

```
spatial-data-platform/
├── .env                  # Environment variables (not tracked in git)
├── .env.example          # Provided dummy of .env file for setup
├── .gitignore            # Git ignore rules
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Dockerfile for the FastAPI app
├── README.md             # Readme file
├── requirements.txt      # Requirements for the FastAPI app
├── app/                  # FastAPI backend application
│   ├── main.py           # Entry point for the FastAPI app
│   ├── api/              # API routes
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── health.py       # Health check route
│   │       │   ├── points.py       # Points API endpoint
│   │       │   ├── polygons.py     # Polygons API endpoint
│   │       │   └── __init__.py     # Init file for versioning
│   ├── config/           # Configuration settings
│   │   ├── settings.py   # Environment variable handling
│   │   └── certs/
│   │       └── aiven_ca.pem  # CA Certificate for secure connections
│   ├── database/         # Database interactions
│   │   ├── db.py         # Database configuration
│   │   └── __init__.py   # Init file for database module
│   ├── middleware/       # FastAPI middleware
│   │   ├── cors.py       # CORS handling
│   │   ├── error_handler.py  # Custom error handling
│   │   ├── gzip.py       # Response compression
│   │   ├── logger.py     # Request logging
│   │   ├── rate_limit.py # Rate limiting
│   │   └── timeout.py    # Request timeout handling
│   ├── models/           # Database models
│   │   ├── point.py      # Point model
│   │   ├── polygon.py    # Polygon model
│   │   └── __init__.py   # Init file for models
│   ├── schemas/          # Data models
│   │   ├── point.py      # Point schema (request/response)
│   │   ├── polygon.py    # Polygon schema (request/response)
│   │   └── response.py   # General response schema
│   ├── services/         # Business logic
│   │   ├── v1/
│   │   │   ├── point_service.py  # Logic for point-related operations
│   │   │   ├── polygon_service.py  # Logic for polygon-related operations
│   │   │   └── __init__.py
└── insomnia_test_apis.json  # Insomnia configuration for API testing
```

## Overview

The **Spatial Data Platform** backend provides two main API functionalities:

1. **Points**: Endpoints to manage geographical points (latitude, longitude).
2. **Polygons**: Endpoints to manage polygons defined by multiple points (e.g., for mapping or spatial queries).

### Features:
- **CRUD Operations** for Points and Polygons.
- **Database Integration**: Connects to a PostgreSQL database to store and retrieve spatial data.
- **API Documentation**: Automatically generated using **FastAPI**'s OpenAPI integration.
- **Insomnia Configuration**: Preconfigured API requests for testing.

## Prerequisites

- Docker and Docker Compose installed ([Docker Desktop](https://www.docker.com/products/docker-desktop) recommended for Windows).
- Python 3.11+ (optional, for local development without Docker).

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Vaibhav-crux/spatial-data-platform.git
cd spatial-data-platform
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory with the following content:

```plaintext
# Database connection details for testing
DB_HOST_TEST=your_test_db_host
DB_PORT_TEST=your_test_db_port
DB_USERNAME_TEST=your_test_db_username
DB_PASSWORD_TEST=your_test_db_password
DB_DATABASE_TEST=your_test_db_name

# Path to the CA certificate
CA_CERT_PATH=app/config/certs/aiven_ca.pem
```

### 3. Build and Run with Docker Compose
```bash
docker-compose up --build
```
This will:
- Build and start the FastAPI backend container.
- Expose the application on port 8000.

### 4. Stop the Application
```bash
docker-compose down
```
Use the `-v` flag to remove volumes as well: `docker-compose down -v`.

## Local Development

If you prefer to run without Docker:

### Backend
1. Navigate to the backend directory:
   ```bash
   cd app
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI app:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Testing with Insomnia

The `insomnia_test_apis.json` file in the root directory contains pre-configured API requests for testing the backend. To import this configuration into Insomnia:

1. **Download and install Insomnia** from [here](https://insomnia.rest/download).
2. **Import the configuration**:
   - Open Insomnia and go to `File` > `Import` > `From File`.
   - Select the `insomnia_test_apis.json` file from the project.
3. **Start Testing**:
   - Once imported, you’ll see all your endpoints (e.g., `/api/v1/points`, `/api/v1/polygons`) pre-configured.
   - You can send requests and view responses to test your FastAPI application.

## API Documentation

Once the app is running, you can access the automatically generated API documentation at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Points
- **POST /api/v1/points/**: Create a new point.
- **GET /api/v1/points/{point_id}**: Retrieve a point by its ID.
- **GET /api/v1/points/**: Retrieve all points.
- **PUT /api/v1/points/{point_id}**: Update a point by ID.
- **PATCH /api/v1/points/{point_id}**: Partially update a point by ID.
- **DELETE /api/v1/points/{point_id}**: Delete a point by ID.

### Polygons
- **POST /api/v1/polygons/**: Create a new polygon.
- **GET /api/v1/polygons/{polygon_id}**: Retrieve a polygon by its ID.
- **GET /api/v1/polygons/**: Retrieve all polygons.
- **PUT /api/v1/polygons/{polygon_id}**: Update a polygon by ID.
- **PATCH /api/v1/polygons/{polygon_id}**: Partially update a polygon by ID.
- **DELETE /api/v1/polygons/{polygon_id}**: Delete a polygon by ID.

## Features
- **Backend**:
  - Supports spatial data (GeoJSON points and polygons).
  - Provides CRUD operations for points and polygons.
  - Logging of requests and errors.
  - Rate limiting and timeout handling.
- **Database**:
  - PostgreSQL with PostGIS for spatial data storage.