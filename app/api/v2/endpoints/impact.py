"""
V2 API endpoints for impact analysis.
Simplified, cleaner API design.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.v2.schemas import GetChildrenRequest, GetChildrenResponse, ChildNode
from app.api.v1.schemas.response import ErrorResponse
from app.api.dependencies import get_graph_repository
from app.application.use_cases.get_children_hierarchy import GetChildrenHierarchyUseCase
from app.domain.repositories import IGraphRepository
from app.core.logging import log
from app.core import exceptions

router = APIRouter()


@router.post(
    "/get-children",
    response_model=List[GetChildrenResponse],
    status_code=status.HTTP_200_OK,
    summary="Get children objects",
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
    },
    tags=["Impact Analysis V2"]
)
async def get_children_objects(
    request: GetChildrenRequest,
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
        log.info(f"[V2] Get children: {request.entity_type}, {len(request.entity_ids)} entities, depth={request.depth}")

        use_case = GetChildrenHierarchyUseCase(graph_repo)
        responses = []

        for entity_id in request.entity_ids:
            result = await use_case.execute(
                entity_type=request.entity_type,
                entity_id=entity_id,
                depth=request.depth
            )

            # Convert to response model
            response = GetChildrenResponse(
                entity_id=result["entity_id"],
                entity_type=result["entity_type"],
                children=[ChildNode(**child) for child in result["children"]],
                total_descendants=result["total_descendants"]
            )
            responses.append(response)

        log.info(f"[V2] Children retrieval complete: {len(responses)} entities processed")
        return responses

    except Exception as e:
        log.error(f"[V2] Error getting children: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="InternalServerError",
                message=f"Failed to get children: {str(e)}",
                details={}
            ).dict()
        )
