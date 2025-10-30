"""
API request schemas (DTOs).
Separates API layer from domain layer following Clean Architecture.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.domain.entities import ChangeType


class AnalyzeImpactRequest(BaseModel):
    """
    Request schema for impact analysis endpoint.

    This DTO translates external API requests to internal domain entities.
    """
    change_type: ChangeType = Field(..., description="Type of change", example="line_specification")
    entity_type: str = Field(..., description="Type of entity being changed", example="Line")
    entity_id: str = Field(..., description="ID of the entity being changed", example="662-LPPL-2014-42\"-AC31-HC")
    description: str = Field(..., description="Description of the change", example="Change pipe specification from 42\" Sch 40 to 42\" Sch 80")
    change_details: Dict[str, Any] = Field(default_factory=dict, description="Additional change details")
    initiated_by: Optional[str] = Field(None, description="User or system initiating change", example="engineer@company.com")
    use_simulation: bool = Field(False, description="Use DES simulation instead of graph traversal")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "change_type": "line_specification",
                "entity_type": "Line",
                "entity_id": "662-LPPL-2014-42\"-AC31-HC",
                "description": "Change pipe specification from 42\" Sch 40 to 42\" Sch 80",
                "change_details": {
                    "old_specification": "42\" Sch 40 AC31",
                    "new_specification": "42\" Sch 80 AC31",
                    "reason": "Pressure rating increase"
                },
                "initiated_by": "engineer@company.com",
                "use_simulation": False
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status")
    database_connected: bool = Field(..., description="Database connection status")
    version: str = Field(..., description="API version")
