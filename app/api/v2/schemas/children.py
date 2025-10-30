"""
V2 API schemas for get-children endpoint.
Returns minimal, recursive structure with id, latest_status, and children.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ChildNode(BaseModel):
    """
    Recursive node structure for impact hierarchy.

    Simple, clean structure showing only essential information:
    - id: Entity identifier
    - latest_status: Current status (if available)
    - children: List of dependent child nodes
    """
    id: str = Field(..., description="Entity ID")
    latest_status: Optional[str] = Field(None, description="Latest status (e.g., for SPOOL: 'fabricated', 'in_progress')")
    children: List['ChildNode'] = Field(default_factory=list, description="List of children nodes")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "SPOOL-001",
                "latest_status": "fabricated",
                "children": []
            }
        }


class GetChildrenRequest(BaseModel):
    """
    Request to get children objects with depth control.

    Depth explanation:
    - depth=1: Direct children only
      Example: ISO -> [SPOOL1, SPOOL2, Part1, Part2]

    - depth=2: Children + grandchildren (2 levels)
      Example: ISO -> SPOOL -> Parts under that spool

    - depth=3+: Continue traversing down the hierarchy
    """
    entity_type: str = Field(..., description="Type of entity (Line, ISO, SPOOL)")
    entity_ids: List[str] = Field(..., description="List of entity IDs to query")
    depth: int = Field(
        1,
        ge=1,
        le=5,
        description="""
        Traversal depth:
        - 1 = Direct children only (ISO -> SPOOLs/Parts)
        - 2 = Children + grandchildren (ISO -> SPOOL -> Parts in spool)
        - 3+ = Continue deeper (if relationships exist)
        """
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "entity_type": "ISO",
                "entity_ids": ["TS002-662-LPPL-2014.SHT1"],
                "depth": 1
            }
        }


class GetChildrenResponse(BaseModel):
    """
    Simplified response showing hierarchical impact structure.

    Each entity shows only:
    - id: Entity identifier
    - latest_status: Current status (when available)
    - children: Recursive list of affected children
    """
    entity_id: str = Field(..., description="The queried entity ID")
    entity_type: str = Field(..., description="Type of the queried entity")
    children: List[ChildNode] = Field(..., description="Hierarchical tree of children")
    total_descendants: int = Field(..., description="Total count of all descendants")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "entity_id": "TS002-662-LPPL-2014.SHT1",
                "entity_type": "ISO",
                "children": [
                    {
                        "id": "SPOOL-001",
                        "latest_status": "fabricated",
                        "children": []
                    },
                    {
                        "id": "Part-001",
                        "latest_status": None,
                        "children": []
                    }
                ],
                "total_descendants": 2
            }
        }


# Enable forward references for recursive model
ChildNode.model_rebuild()
