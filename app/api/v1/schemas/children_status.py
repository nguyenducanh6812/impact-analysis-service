"""
V1 API schemas for getting children status.
Generic - works for any entity type (LINE, ISO, SPOOL).
Returns hierarchical tree with id, type, status, and recursive children.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class GetChildrenStatusRequest(BaseModel):
    """
    Request to get children of any entity.

    Simple input: just provide the entity ID(s).
    Works for LINE, ISO, SPOOL, or any other entity type.
    """
    entity_ids: List[str] = Field(
        ...,
        description="List of entity IDs to query (LINE, ISO, SPOOL, etc.)",
        min_length=1
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "entity_ids": ["TS002-662-LPPL-2014.SHT1"]
            }
        }


class ChildNode(BaseModel):
    """
    Hierarchical child node with id, type, status, and recursive children.
    """
    id: str = Field(..., description="Child entity ID")
    type: str = Field(..., description="Entity type (ISO, SPOOL, Part, etc.)")
    status: Optional[str] = Field(None, description="Current status (if available)")
    children: List['ChildNode'] = Field(default_factory=list, description="Recursive children")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "TS002-662-LPPL-2014.SHT5/SP01",
                "type": "SPOOL",
                "status": "fabricated",
                "children": [
                    {
                        "id": "ELBOW 1 of BRANCH /TS002-662-LPPL-2014.SHT5/B1",
                        "type": "Part",
                        "status": None,
                        "children": []
                    }
                ]
            }
        }

# Enable forward reference for recursive model
ChildNode.model_rebuild()


class ChildrenStatusResponse(BaseModel):
    """
    Response containing entity children in hierarchical tree structure.

    Returns id, type, status, and recursive children.
    Works for any entity type.
    """
    entity_id: str = Field(..., description="The entity ID that was queried")
    entity_type: str = Field(..., description="The entity type that was queried")
    children: List[ChildNode] = Field(..., description="Hierarchical tree of children")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "entity_id": "TS002-662-LPPL-2014.SHT1",
                "entity_type": "ISO",
                "children": [
                    {
                        "id": "TS002-662-LPPL-2014.SHT5/SP01",
                        "type": "SPOOL",
                        "status": "fabricated",
                        "children": [
                            {
                                "id": "ELBOW 1 of BRANCH /TS002-662-LPPL-2014.SHT5/B1",
                                "type": "Part",
                                "status": None,
                                "children": []
                            },
                            {
                                "id": "FLANGE 3 of BRANCH /TS002-662-LPPL-2014.SHT5/B1",
                                "type": "Part",
                                "status": None,
                                "children": []
                            }
                        ]
                    }
                ]
            }
        }
