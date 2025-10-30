"""
Camunda-specific response schemas.
Optimized for Camunda DMN decision-making.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class EntitySummary(BaseModel):
    """Summary of an entity."""
    id: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class ImpactHierarchy(BaseModel):
    """
    Hierarchical representation of impact.

    Represents the tree structure: Line -> ISOs -> Spools -> Parts
    """
    entity_id: str
    entity_type: str
    children: List['ImpactHierarchy'] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    impact_count: int = 0


class CamundaImpactResponse(BaseModel):
    """
    Response format optimized for Camunda workflow.

    Includes decision-making variables for DMN tables.
    """
    # Summary metrics for DMN decision
    total_affected_isos: int = Field(0, description="Total ISOs affected")
    total_affected_spools: int = Field(0, description="Total spools affected")
    total_affected_parts: int = Field(0, description="Total parts affected")
    total_impact_count: int = Field(0, description="Total affected objects")

    # Decision variables
    severity: str = Field("low", description="Impact severity: low, medium, high, critical")
    requires_approval: bool = Field(False, description="Whether approval is required")
    estimated_cost_impact: Optional[float] = Field(None, description="Estimated cost impact (future)")
    estimated_schedule_impact_days: Optional[float] = Field(None, description="Estimated schedule impact")

    # Detailed impact data
    affected_lines: List[EntitySummary] = Field(default_factory=list)
    affected_isos: List[EntitySummary] = Field(default_factory=list)
    affected_spools: List[EntitySummary] = Field(default_factory=list)
    affected_parts: List[EntitySummary] = Field(default_factory=list)

    # Hierarchical view (for visualization)
    impact_hierarchy: List[ImpactHierarchy] = Field(default_factory=list)

    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_method: str = Field("graph_traversal")

    # Camunda process variables
    camunda_variables: Dict[str, Any] = Field(default_factory=dict, description="Variables for Camunda process")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "total_affected_isos": 7,
                "total_affected_spools": 12,
                "total_affected_parts": 45,
                "total_impact_count": 64,
                "severity": "high",
                "requires_approval": True,
                "affected_isos": [
                    {"id": "TS002-662-LPPL-2014.SHT1", "type": "ISO", "properties": {}},
                    {"id": "TS002-662-LPPL-2014.SHT2", "type": "ISO", "properties": {}}
                ],
                "camunda_variables": {
                    "impactSeverity": "high",
                    "requiresApproval": True,
                    "affectedISOCount": 7
                }
            }
        }


class ChildrenResponse(BaseModel):
    """
    Response for getting children objects.

    Returns hierarchical structure of dependent objects.
    """
    entity_type: str
    entity_id: str
    direct_children: List[EntitySummary] = Field(default_factory=list)
    all_descendants: List[EntitySummary] = Field(default_factory=list)
    hierarchy: ImpactHierarchy
    total_count: int = 0

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "entity_type": "Line",
                "entity_id": "662-LPPL-2014-42\"-AC31-HC",
                "direct_children": [
                    {"id": "TS002-662-LPPL-2014.SHT1", "type": "ISO", "properties": {}},
                    {"id": "TS002-662-LPPL-2014.SHT2", "type": "ISO", "properties": {}}
                ],
                "total_count": 7
            }
        }


# Enable forward references
ImpactHierarchy.model_rebuild()
