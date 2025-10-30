"""
Line entity - represents a piping line in the engineering project.
Domain model following DDD principles.
"""
from pydantic import BaseModel, Field
from typing import Optional


class Line(BaseModel):
    """
    Line entity representing a piping line.

    Attributes:
        id: Unique identifier (line_number)
        line_number: Line identification number
        system_number: System this line belongs to
        system_name: Name of the system
        project_number: Project identifier
        project_name: Project name
        module_name: Module identifier
    """
    id: str = Field(..., description="Unique line identifier")
    line_number: str = Field(..., description="Line number")
    system_number: int = Field(..., description="System number")
    system_name: str = Field(..., description="System name")
    project_number: str = Field(..., description="Project number")
    project_name: str = Field(..., description="Project name")
    module_name: str = Field(..., description="Module name")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "662-LPPL-2014-42\"-AC31-HC",
                "line_number": "662-LPPL-2014-42\"-AC31-HC",
                "system_number": 662,
                "system_name": "OIL SEPARATION AND STABILIZATION",
                "project_number": "SO17113",
                "project_name": "FPSO",
                "module_name": "TS002"
            }
        }
