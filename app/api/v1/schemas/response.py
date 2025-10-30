"""
API response schemas (DTOs).
Separates API layer from domain layer following Clean Architecture.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities import ChangeSeverity


class ISOResponse(BaseModel):
    """Response schema for ISO entity."""
    id: str
    iso_number: Optional[str] = None
    sheet_number: Optional[str] = None


class ImpactAnalysisResponse(BaseModel):
    """
    Response schema for impact analysis endpoint.

    This DTO translates internal domain entities to external API responses.
    """
    event_id: Optional[str] = Field(None, description="Change event ID")
    affected_isos: List[ISOResponse] = Field(default_factory=list, description="List of affected ISOs")
    affected_spools: List[Dict[str, Any]] = Field(default_factory=list, description="List of affected spools")
    affected_parts: List[Dict[str, Any]] = Field(default_factory=list, description="List of affected parts")
    impact_count: int = Field(..., description="Total number of affected items")
    severity: Optional[ChangeSeverity] = Field(None, description="Impact severity")
    estimated_delay_days: Optional[float] = Field(None, description="Estimated timeline delay in days")
    analysis_timestamp: datetime = Field(..., description="When the analysis was performed")
    analysis_method: str = Field(..., description="Method used for analysis")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Additional analysis information")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "event_id": "CHG-2024-001",
                "affected_isos": [
                    {"id": "TS002-662-LPPL-2014.SHT1", "iso_number": "TS002-662-LPPL-2014", "sheet_number": "SHT1"},
                    {"id": "TS002-662-LPPL-2014.SHT2", "iso_number": "TS002-662-LPPL-2014", "sheet_number": "SHT2"}
                ],
                "affected_spools": [],
                "affected_parts": [],
                "impact_count": 7,
                "severity": "high",
                "estimated_delay_days": None,
                "analysis_timestamp": "2024-10-14T10:30:00Z",
                "analysis_method": "graph_traversal",
                "additional_info": {
                    "line_id": "662-LPPL-2014-42\"-AC31-HC",
                    "total_isos": 7,
                    "total_spools": 0,
                    "total_parts": 0
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "error": "EntityNotFoundError",
                "message": "Line not found: INVALID-LINE-ID",
                "details": {"line_id": "INVALID-LINE-ID"},
                "timestamp": "2024-10-14T10:30:00Z"
            }
        }
