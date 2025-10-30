"""
ChangeEvent entity - represents a change event in the engineering project.
Domain model following DDD principles.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ChangeType(str, Enum):
    """Types of engineering changes."""
    LINE_SPECIFICATION = "line_specification"
    ISO_REVISION = "iso_revision"
    EQUIPMENT_MODIFICATION = "equipment_modification"
    MATERIAL_CHANGE = "material_change"
    PIPING_ROUTING = "piping_routing"
    OTHER = "other"


class ChangeSeverity(str, Enum):
    """Severity levels for impact assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeEvent(BaseModel):
    """
    ChangeEvent entity representing an engineering change.

    Attributes:
        event_id: Unique identifier for the change event
        change_type: Type of change
        entity_type: Type of entity being changed (Line, ISO, Equipment, etc.)
        entity_id: ID of the entity being changed
        description: Description of the change
        change_details: Additional details about the change
        severity: Assessed severity of the change impact
        timestamp: When the change was initiated
        initiated_by: User or system that initiated the change
    """
    event_id: Optional[str] = Field(None, description="Unique event identifier")
    change_type: ChangeType = Field(..., description="Type of change")
    entity_type: str = Field(..., description="Type of entity (Line, ISO, etc.)")
    entity_id: str = Field(..., description="ID of the entity being changed")
    description: str = Field(..., description="Change description")
    change_details: Dict[str, Any] = Field(default_factory=dict, description="Additional change details")
    severity: Optional[ChangeSeverity] = Field(None, description="Impact severity")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Change timestamp")
    initiated_by: Optional[str] = Field(None, description="User or system initiating change")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "event_id": "CHG-2024-001",
                "change_type": "line_specification",
                "entity_type": "Line",
                "entity_id": "662-LPPL-2014-42\"-AC31-HC",
                "description": "Change pipe specification from 42\" Sch 40 to 42\" Sch 80",
                "change_details": {
                    "old_specification": "42\" Sch 40 AC31",
                    "new_specification": "42\" Sch 80 AC31",
                    "reason": "Pressure rating increase"
                },
                "severity": "high",
                "initiated_by": "john.doe@company.com"
            }
        }
