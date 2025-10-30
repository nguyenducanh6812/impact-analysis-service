"""
Impact Analysis Service - Main Application
FastAPI microservice for analyzing engineering change impacts.

Architecture: Clean Architecture with SOLID principles
- Domain Layer: Entities, repositories (interfaces)
- Application Layer: Use cases, strategies
- Infrastructure Layer: Database implementations
- Presentation Layer: API endpoints, DTOs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.endpoints import impact, camunda
from app.api.v2.endpoints import impact as impact_v2
from app.infrastructure.database import neo4j_client
from app.core.config import settings
from app.core.logging import log


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    log.info(f"Starting {settings.app_name} v{settings.app_version}")

    try:
        # Connect to Neo4j
        await neo4j_client.connect()
        log.info("Database connection established")
    except Exception as e:
        log.error(f"Failed to connect to database: {str(e)}")

    yield

    # Shutdown
    log.info("Shutting down application")
    await neo4j_client.close()
    log.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    Microservice for analyzing the impact of engineering changes on dependent entities
    using graph traversal and discrete event simulation.

    **API Versions:**
    - V1: Full-featured API with detailed responses
    - V2: Simplified API with minimal, clean responses (Recommended for new integrations)

    **Documentation:**
    - V1 Docs: /api/v1/docs
    - V2 Docs: /api/v2/docs
    """,
    version=settings.app_version,
    docs_url="/docs",  # Root level docs showing all APIs
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    impact.router,
    prefix=settings.api_v1_prefix,
    tags=["Impact Analysis"]
)

app.include_router(
    camunda.router,
    prefix=settings.api_v1_prefix,
    tags=["Camunda Integration (V1)"]
)

# V2 API
app.include_router(
    impact_v2.router,
    prefix=settings.api_v2_prefix,
    tags=["Impact Analysis V2"]
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "api_v1_docs": f"{settings.api_v1_prefix}/docs",
        "api_v2_docs": f"{settings.api_v2_prefix}/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
