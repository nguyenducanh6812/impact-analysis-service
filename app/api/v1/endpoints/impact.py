"""
Impact analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas import (
    AnalyzeImpactRequest,
    ImpactAnalysisResponse,
    ErrorResponse,
    ISOResponse,
    HealthCheckResponse
)
from app.api.dependencies import (
    get_analyze_impact_use_case,
    get_analyze_impact_use_case_with_simulation,
    get_graph_repository
)
from app.application.use_cases import AnalyzeLineImpactUseCase
from app.domain.entities import ChangeEvent
from app.domain.repositories import IGraphRepository
from app.core.logging import log
from app.core.config import settings
from app.core import exceptions
from datetime import datetime

router = APIRouter()


@router.post(
    "/analyze-impact",
    response_model=ImpactAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze change impact",
    description="Analyzes the impact of an engineering change on dependent entities",
    responses={
        200: {"description": "Impact analysis completed successfully"},
        404: {"model": ErrorResponse, "description": "Entity not found"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def analyze_impact(
    request: AnalyzeImpactRequest,
    use_case: AnalyzeLineImpactUseCase = Depends(get_analyze_impact_use_case)
):
    """
    Analyze the impact of an engineering change.

    This endpoint receives a change event and returns all affected entities
    (ISOs, spools, parts) along with severity assessment.

    Args:
        request: Impact analysis request
        use_case: Injected use case instance

    Returns:
        ImpactAnalysisResponse with analysis results
    """
    try:
        log.info(f"Received impact analysis request for {request.entity_type}:{request.entity_id}")

        # Convert request DTO to domain entity
        change_event = ChangeEvent(
            change_type=request.change_type,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            description=request.description,
            change_details=request.change_details,
            initiated_by=request.initiated_by
        )

        # Execute use case
        result = await use_case.execute(change_event)

        # Convert domain entity to response DTO
        response = ImpactAnalysisResponse(
            event_id=result.event_id,
            affected_isos=[ISOResponse(**iso.dict()) for iso in result.affected_isos],
            affected_spools=result.affected_spools,
            affected_parts=result.affected_parts,
            impact_count=result.impact_count,
            severity=result.severity,
            estimated_delay_days=result.estimated_delay_days,
            analysis_timestamp=result.analysis_timestamp,
            analysis_method=result.analysis_method,
            additional_info=result.additional_info
        )

        log.info(f"Impact analysis completed: {response.impact_count} entities affected")
        return response

    except exceptions.EntityNotFoundError as e:
        log.error(f"Entity not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(
                error="EntityNotFoundError",
                message=e.message,
                details=e.details
            ).dict()
        )

    except exceptions.InvalidChangeEventError as e:
        log.error(f"Invalid change event: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error="InvalidChangeEventError",
                message=e.message,
                details=e.details
            ).dict()
        )

    except exceptions.DatabaseConnectionError as e:
        log.error(f"Database error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="DatabaseConnectionError",
                message=e.message,
                details=e.details
            ).dict()
        )

    except Exception as e:
        log.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="InternalServerError",
                message=f"An unexpected error occurred: {str(e)}",
                details={}
            ).dict()
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check service and database health"
)
async def health_check(
    graph_repo: IGraphRepository = Depends(get_graph_repository)
):
    """
    Health check endpoint.

    Verifies service status and database connectivity.

    Args:
        graph_repo: Injected graph repository

    Returns:
        HealthCheckResponse with service status
    """
    try:
        db_connected = await graph_repo.check_connection()

        return HealthCheckResponse(
            status="healthy" if db_connected else "degraded",
            database_connected=db_connected,
            version=settings.app_version
        )
    except Exception as e:
        log.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            database_connected=False,
            version=settings.app_version
        )
