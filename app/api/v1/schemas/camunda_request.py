"""
Camunda-specific request schemas.
Designed for integration with Camunda BPMN workflows.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class BatchImpactAnalysisRequest(BaseModel):
    """
    Request schema for batch impact analysis.

    Receives lists of line numbers and ISO numbers from Camunda,
    returns all affected children objects.
    """
    line_numbers: List[str] = Field(default_factory=list, description="List of line numbers to analyze")
    iso_numbers: List[str] = Field(default_factory=list, description="List of ISO numbers to analyze")
    include_spools: bool = Field(True, description="Include affected spools in response")
    include_parts: bool = Field(True, description="Include affected parts in response")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "line_numbers": [
                    "662-LPPL-2014-42\"-AC31-HC",
                    "662-LPPL-2015-24\"-AC31-HC"
                ],
                "iso_numbers": [
                    "TS002-662-LPPL-2014.SHT1"
                ],
                "include_spools": True,
                "include_parts": True
            }
        }


class GetChildrenRequest(BaseModel):
    """
    Request to get children objects of specific entities.

    For Camunda to get hierarchical impact data.
    """
    entity_type: str = Field(..., description="Type of entity (Line or ISO)")
    entity_ids: List[str] = Field(..., description="List of entity IDs")
    depth: int = Field(1, description="How many levels deep to traverse (1=direct children, 2=children+grandchildren)")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "entity_type": "Line",
                "entity_ids": ["662-LPPL-2014-42\"-AC31-HC"],
                "depth": 2
            }
        }
