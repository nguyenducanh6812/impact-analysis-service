"""
Camunda integration endpoints.
Optimized for Camunda BPMN workflow and DMN decision-making.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.v1.schemas.camunda_request import (
    BatchImpactAnalysisRequest,
    GetChildrenRequest
)
from app.api.v1.schemas.camunda_response import (
    CamundaImpactResponse,
    ChildrenResponse,
    EntitySummary,
    ImpactHierarchy
)
from app.api.v1.schemas.children_schema import (
    GetChildrenRequestV2,
    GetChildrenResponseV2,
    ChildNode as ChildNodeV2
)
from app.api.v1.schemas.children_status import (
    GetChildrenStatusRequest,
    ChildrenStatusResponse,
    ChildNode as ChildNodeV1
)
from app.api.v1.schemas.response import ErrorResponse
from app.api.dependencies import get_graph_repository
from app.application.use_cases.batch_impact_analysis import BatchImpactAnalysisUseCase
from app.application.use_cases.get_children_hierarchy import GetChildrenHierarchyUseCase
from app.application.use_cases.get_children_status import GetChildrenStatusUseCase
from app.domain.repositories import IGraphRepository
from app.domain.entities import ISO
from app.core.logging import log
from app.core import exceptions

router = APIRouter()


@router.post(
    "/batch-analyze-impact",
    response_model=CamundaImpactResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch impact analysis for Camunda",
    description="Analyzes impact of multiple lines and ISOs, returns decision variables for Camunda DMN",
    responses={
        200: {"description": "Batch analysis completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def batch_analyze_impact(
    request: BatchImpactAnalysisRequest,
    graph_repo: IGraphRepository = Depends(get_graph_repository)
):
    """
    Analyze impact of multiple lines and ISOs in a single request.

    This endpoint is optimized for Camunda BPMN integration:
    - Receives lists of line numbers and ISO numbers
    - Returns all affected children (ISOs, spools, parts)
    - Provides decision variables for DMN tables
    - Includes severity assessment and approval requirements

    Args:
        request: Batch analysis request with line and ISO lists
        graph_repo: Injected graph repository

    Returns:
        CamundaImpactResponse with complete impact analysis and decision variables
    """
    try:
        log.info(f"Camunda batch analysis: {len(request.line_numbers)} lines, {len(request.iso_numbers)} ISOs")

        # Create use case
        use_case = BatchImpactAnalysisUseCase(graph_repo)

        # Execute analysis
        result = await use_case.execute(
            line_numbers=request.line_numbers,
            iso_numbers=request.iso_numbers,
            include_spools=request.include_spools,
            include_parts=request.include_parts
        )

        # Calculate severity
        total_impact = result["metrics"]["total_impact_count"]
        severity = use_case._assess_severity(total_impact)
        requires_approval = use_case._requires_approval(severity, total_impact)

        # Build Camunda response
        response = CamundaImpactResponse(
            total_affected_isos=result["metrics"]["total_affected_isos"],
            total_affected_spools=result["metrics"]["total_affected_spools"],
            total_affected_parts=result["metrics"]["total_affected_parts"],
            total_impact_count=total_impact,
            severity=severity,
            requires_approval=requires_approval,
            affected_lines=[EntitySummary(**item) for item in result["affected_lines"]],
            affected_isos=[EntitySummary(**item) for item in result["affected_isos"]],
            affected_spools=[EntitySummary(**item) for item in result["affected_spools"]],
            affected_parts=[EntitySummary(**item) for item in result["affected_parts"]],
            impact_hierarchy=[ImpactHierarchy(**item) for item in result["impact_hierarchy"]],
            analysis_method="graph_traversal",
            camunda_variables={
                "impactSeverity": severity,
                "requiresApproval": requires_approval,
                "affectedISOCount": result["metrics"]["total_affected_isos"],
                "affectedSpoolCount": result["metrics"]["total_affected_spools"],
                "affectedPartCount": result["metrics"]["total_affected_parts"],
                "totalImpactCount": total_impact,
                "outcome": "IMPACT" if total_impact > 0 else "NO_IMPACT"
            }
        )

        log.info(f"Batch analysis complete: {total_impact} impacts, severity={severity}, approval={requires_approval}")
        return response

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
        log.error(f"Unexpected error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="InternalServerError",
                message=f"Batch analysis failed: {str(e)}",
                details={}
            ).dict()
        )


@router.post(
    "/get-children-status",
    response_model=List[ChildrenStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Get children status for any entity (hierarchical tree)",
    description="""
    Get children with their status for any entity type (LINE, ISO, SPOOL) in hierarchical tree structure.

    **Simple Input:** Just provide entity ID(s) - no need to specify type
    **Tree Output:** Returns hierarchical tree with `id`, `type`, `status`, and nested `children`

    **How it works (Hierarchical):**
    - LINE input → returns ISOs tree
    - ISO input → returns SPOOLs tree (with Parts nested inside each SPOOL)
    - SPOOL input → returns Parts tree

    **Example Output for ISO:**
    ```json
    {
      "entity_id": "TS002-662-LPPL-2014.SHT1",
      "entity_type": "ISO",
      "children": [
        {
          "id": "TS002-662-LPPL-2014.SHT5/SP01",
          "type": "SPOOL",
          "status": "fabricated",
          "children": [
            {"id": "ELBOW 1", "type": "Part", "status": null, "children": []},
            {"id": "FLANGE 3", "type": "Part", "status": null, "children": []}
          ]
        }
      ]
    }
    ```

    Perfect for visualizing the complete impact hierarchy when any entity changes.
    """,
    responses={
        200: {"description": "Children status retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_children_status(
    request: GetChildrenStatusRequest,
    graph_repo: IGraphRepository = Depends(get_graph_repository)
):
    """
    Get children for any entity type in hierarchical tree structure.

    Returns id, type, status, and recursive children.

    Args:
        request: Request with list of entity IDs
        graph_repo: Injected graph repository

    Returns:
        List of ChildrenStatusResponse with hierarchical tree structure

    Example:
        Input: {"entity_ids": ["TS002-662-LPPL-2014.SHT1"]}
        Output: [
          {
            "entity_id": "TS002-662-LPPL-2014.SHT1",
            "entity_type": "ISO",
            "children": [
              {
                "id": "TS002-662-LPPL-2014.SHT5/SP01",
                "type": "SPOOL",
                "status": "fabricated",
                "children": [
                  {"id": "ELBOW 1", "type": "Part", "status": null, "children": []},
                  {"id": "FLANGE 3", "type": "Part", "status": null, "children": []}
                ]
              }
            ]
          }
        ]
    """
    try:
        log.info(f"[V1] Get children status (hierarchical): {len(request.entity_ids)} entities")

        use_case = GetChildrenStatusUseCase(graph_repo)
        responses = []

        for entity_id in request.entity_ids:
            result = await use_case.execute(entity_id)

            # Convert to response model with recursive children
            def build_child_nodes(children_data):
                return [ChildNodeV1(**child) for child in children_data]

            response = ChildrenStatusResponse(
                entity_id=result["entity_id"],
                entity_type=result["entity_type"],
                children=build_child_nodes(result["children"])
            )
            responses.append(response)

        log.info(f"[V1] Children status retrieval complete: {len(responses)} entities processed")
        return responses

    except Exception as e:
        log.error(f"[V1] Error getting children status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="InternalServerError",
                message=f"Failed to get children status: {str(e)}",
                details={}
            ).dict()
        )


@router.post(
    "/get-children-v2",
    response_model=List[GetChildrenResponseV2],
    status_code=status.HTTP_200_OK,
    summary="Get children objects (Simplified)",
    description="""
    Get children objects in a simplified, recursive format.

    **Depth Parameter:**
    - depth=1: Direct children only
      - ISO -> [SPOOL, SPOOL, Part, Part]
    - depth=2: Children + grandchildren
      - ISO -> SPOOL -> [Parts in that spool]
    - depth=3+: Continue traversing (if more relationships exist)

    **Response Format:**
    Returns minimal data for each node:
    - id: Entity identifier
    - latest_status: Current status (e.g., SPOOL status: "fabricated", "in_progress")
    - children: Recursive list of affected children

    **Example Use Case:**
    When ISO changes, you can see:
    - Which SPOOLs are affected (with their status)
    - Which Parts are affected
    - The complete hierarchy of impacts
    """,
    responses={
        200: {"description": "Children retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_children_objects_v2(
    request: GetChildrenRequestV2,
    graph_repo: IGraphRepository = Depends(get_graph_repository)
):
    """
    Get children objects in simplified format with only id, latest_status, and children.

    This endpoint returns a clean, recursive structure perfect for:
    - Impact visualization
    - Status tracking
    - Change propagation analysis

    Args:
        request: Request with entity type, IDs, and traversal depth
        graph_repo: Injected graph repository

    Returns:
        List of simplified hierarchy responses

    Example:
        Input: ISO "TS002-662-LPPL-2014.SHT1", depth=1
        Output:
        [
          {
            "entity_id": "TS002-662-LPPL-2014.SHT1",
            "entity_type": "ISO",
            "children": [
              {"id": "SPOOL-001", "latest_status": "fabricated", "children": []},
              {"id": "SPOOL-002", "latest_status": "in_progress", "children": []},
              {"id": "Part-001", "latest_status": null, "children": []}
            ],
            "total_descendants": 3
          }
        ]
    """
    try:
        log.info(f"Get children v2: {request.entity_type}, {len(request.entity_ids)} entities, depth={request.depth}")

        use_case = GetChildrenHierarchyUseCase(graph_repo)
        responses = []

        for entity_id in request.entity_ids:
            result = await use_case.execute(
                entity_type=request.entity_type,
                entity_id=entity_id,
                depth=request.depth
            )

            # Convert to response model
            response = GetChildrenResponseV2(
                entity_id=result["entity_id"],
                entity_type=result["entity_type"],
                children=[ChildNodeV2(**child) for child in result["children"]],
                total_descendants=result["total_descendants"]
            )
            responses.append(response)

        log.info(f"Children v2 retrieval complete: {len(responses)} entities processed")
        return responses

    except Exception as e:
        log.error(f"Error getting children v2: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="InternalServerError",
                message=f"Failed to get children: {str(e)}",
                details={}
            ).dict()
        )
