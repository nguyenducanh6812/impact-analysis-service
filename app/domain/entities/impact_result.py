"""
ImpactResult entity - represents the result of an impact analysis.
Domain model following DDD principles.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entities.iso import ISO
from app.domain.entities.change_event import ChangeSeverity


class ImpactResult(BaseModel):
    """
    ImpactResult entity containing the analysis results.

    Attributes:
        event_id: Reference to the change event
        affected_isos: List of affected isometric drawings
        affected_spools: List of affected fabrication spools (future)
        affected_parts: List of affected parts (future)
        impact_count: Total number of affected items
        severity: Overall impact severity
        estimated_delay_days: Estimated timeline delay (for DES)
        analysis_timestamp: When the analysis was performed
        analysis_method: Method used (graph_traversal or simulation)
        additional_info: Any additional analysis information
    """
    event_id: Optional[str] = Field(None, description="Change event ID")
    affected_isos: List[ISO] = Field(default_factory=list, description="Affected ISOs")
    affected_spools: List[Dict[str, Any]] = Field(default_factory=list, description="Affected spools")
    affected_parts: List[Dict[str, Any]] = Field(default_factory=list, description="Affected parts")
    impact_count: int = Field(0, description="Total affected items")
    severity: Optional[ChangeSeverity] = Field(None, description="Overall severity")
    estimated_delay_days: Optional[float] = Field(None, description="Estimated delay in days")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis time")
    analysis_method: str = Field("graph_traversal", description="Analysis method used")
    additional_info: Dict[str, Any] = Field(default_factory=dict, description="Additional information")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "event_id": "CHG-2024-001",
                "affected_isos": [
                    {"id": "TS002-662-LPPL-2014.SHT1", "iso_number": "TS002-662-LPPL-2014", "sheet_number": "SHT1"},
                    {"id": "TS002-662-LPPL-2014.SHT2", "iso_number": "TS002-662-LPPL-2014", "sheet_number": "SHT2"}
                ],
                "impact_count": 7,
                "severity": "high",
                "estimated_delay_days": 14.5,
                "analysis_method": "graph_traversal",
                "additional_info": {
                    "total_isos": 7,
                    "total_spools": 0,
                    "total_parts": 0
                }
            }
        }

    def calculate_impact_count(self) -> int:
        """Calculate total impact count across all affected items."""
        return (
            len(self.affected_isos) +
            len(self.affected_spools) +
            len(self.affected_parts)
        )

    def update_impact_count(self):
        """Update the impact_count field."""
        self.impact_count = self.calculate_impact_count()
