"""
ISO (Isometric) entity - represents an isometric drawing.
Domain model following DDD principles.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ISO(BaseModel):
    """
    ISO entity representing an isometric drawing.

    Attributes:
        id: Unique identifier for the isometric
        iso_number: Isometric drawing number
        sheet_number: Sheet number if multi-sheet drawing
    """
    id: str = Field(..., description="Unique ISO identifier")
    iso_number: Optional[str] = Field(None, description="ISO drawing number")
    sheet_number: Optional[str] = Field(None, description="Sheet number")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "TS002-662-LPPL-2014.SHT1",
                "iso_number": "TS002-662-LPPL-2014",
                "sheet_number": "SHT1"
            }
        }

    @classmethod
    def parse_iso_id(cls, iso_id: str) -> dict:
        """
        Parse ISO ID into components.

        Args:
            iso_id: Full ISO identifier (e.g., 'TS002-662-LPPL-2014.SHT1')

        Returns:
            Dictionary with iso_number and sheet_number
        """
        parts = iso_id.split('.')
        iso_number = parts[0] if len(parts) > 0 else iso_id
        sheet_number = parts[1] if len(parts) > 1 else None

        return {
            "id": iso_id,
            "iso_number": iso_number,
            "sheet_number": sheet_number
        }
