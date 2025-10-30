"""
Batch Impact Analysis Use Case.
Analyzes multiple lines and ISOs in a single request for Camunda integration.
"""
from typing import List, Dict, Any
from app.domain.repositories import IGraphRepository
from app.domain.entities import ISO, Line
from app.core.logging import log
from app.core.exceptions import EntityNotFoundError


class BatchImpactAnalysisUseCase:
    """
    Use case for analyzing impact of multiple entities in batch.

    Designed for Camunda BPMN workflow integration.
    """

    def __init__(self, graph_repository: IGraphRepository):
        """
        Initialize use case with graph repository.

        Args:
            graph_repository: Repository for graph operations
        """
        self.graph_repo = graph_repository

    async def execute(
        self,
        line_numbers: List[str],
        iso_numbers: List[str],
        include_spools: bool = True,
        include_parts: bool = True
    ) -> Dict[str, Any]:
        """
        Execute batch impact analysis.

        Args:
            line_numbers: List of line IDs to analyze
            iso_numbers: List of ISO IDs to analyze
            include_spools: Whether to include spools
            include_parts: Whether to include parts

        Returns:
            Dictionary with all affected entities and metrics
        """
        log.info(f"Batch analysis: {len(line_numbers)} lines, {len(iso_numbers)} ISOs")

        result = {
            "affected_lines": [],
            "affected_isos": [],
            "affected_spools": [],
            "affected_parts": [],
            "impact_hierarchy": [],
            "metrics": {
                "total_affected_isos": 0,
                "total_affected_spools": 0,
                "total_affected_parts": 0,
                "total_impact_count": 0
            }
        }

        # Process lines
        for line_id in line_numbers:
            await self._process_line(line_id, result, include_spools, include_parts)

        # Process ISOs
        for iso_id in iso_numbers:
            await self._process_iso(iso_id, result, include_spools, include_parts)

        # Calculate metrics
        result["metrics"]["total_affected_isos"] = len(result["affected_isos"])
        result["metrics"]["total_affected_spools"] = len(result["affected_spools"])
        result["metrics"]["total_affected_parts"] = len(result["affected_parts"])
        result["metrics"]["total_impact_count"] = (
            len(result["affected_isos"]) +
            len(result["affected_spools"]) +
            len(result["affected_parts"])
        )

        log.info(f"Batch analysis complete: {result['metrics']['total_impact_count']} total impacts")
        return result

    async def _process_line(
        self,
        line_id: str,
        result: Dict[str, Any],
        include_spools: bool,
        include_parts: bool
    ):
        """Process a single line and its impacts."""
        try:
            # Get line entity
            line = await self.graph_repo.get_line_by_id(line_id)
            if not line:
                log.warning(f"Line not found: {line_id}")
                return

            # Add to affected lines
            result["affected_lines"].append({
                "id": line.id,
                "type": "Line",
                "properties": line.dict()
            })

            # Get affected ISOs
            isos = await self.graph_repo.get_affected_isos_by_line(line_id)

            # Build hierarchy
            hierarchy_node = {
                "entity_id": line_id,
                "entity_type": "Line",
                "children": [],
                "properties": line.dict(),
                "impact_count": 0
            }

            for iso in isos:
                # Add to affected ISOs (avoid duplicates)
                if not any(i["id"] == iso.id for i in result["affected_isos"]):
                    result["affected_isos"].append({
                        "id": iso.id,
                        "type": "ISO",
                        "properties": iso.dict()
                    })

                # Process ISO children
                iso_children = await self._get_iso_children(
                    iso.id,
                    result,
                    include_spools,
                    include_parts
                )

                hierarchy_node["children"].append(iso_children)

            # Calculate impact count for this line
            hierarchy_node["impact_count"] = self._count_hierarchy_impacts(hierarchy_node)
            result["impact_hierarchy"].append(hierarchy_node)

        except Exception as e:
            log.error(f"Error processing line {line_id}: {str(e)}")

    async def _process_iso(
        self,
        iso_id: str,
        result: Dict[str, Any],
        include_spools: bool,
        include_parts: bool
    ):
        """Process a single ISO and its impacts."""
        try:
            # Add to affected ISOs if not already present
            if not any(i["id"] == iso_id for i in result["affected_isos"]):
                iso_data = ISO.parse_iso_id(iso_id)
                result["affected_isos"].append({
                    "id": iso_id,
                    "type": "ISO",
                    "properties": iso_data
                })

            # Get ISO children
            iso_hierarchy = await self._get_iso_children(
                iso_id,
                result,
                include_spools,
                include_parts
            )

            result["impact_hierarchy"].append(iso_hierarchy)

        except Exception as e:
            log.error(f"Error processing ISO {iso_id}: {str(e)}")

    async def _get_iso_children(
        self,
        iso_id: str,
        result: Dict[str, Any],
        include_spools: bool,
        include_parts: bool
    ) -> Dict[str, Any]:
        """Get children of an ISO (spools and parts)."""
        iso_data = ISO.parse_iso_id(iso_id)
        hierarchy_node = {
            "entity_id": iso_id,
            "entity_type": "ISO",
            "children": [],
            "properties": iso_data,
            "impact_count": 0
        }

        # Get spools
        if include_spools:
            spools = await self.graph_repo.get_affected_spools_by_iso(iso_id)
            for spool in spools:
                if not any(s["id"] == spool.get("id") for s in result["affected_spools"]):
                    result["affected_spools"].append({
                        "id": spool.get("id", "unknown"),
                        "type": "SPOOL",
                        "properties": spool
                    })

                hierarchy_node["children"].append({
                    "entity_id": spool.get("id", "unknown"),
                    "entity_type": "SPOOL",
                    "children": [],
                    "properties": spool,
                    "impact_count": 1
                })

        # Get parts
        if include_parts:
            parts = await self.graph_repo.get_affected_parts_by_iso(iso_id)
            for part in parts:
                if not any(p["id"] == part.get("id") for p in result["affected_parts"]):
                    result["affected_parts"].append({
                        "id": part.get("id", "unknown"),
                        "type": "Part",
                        "properties": part
                    })

                hierarchy_node["children"].append({
                    "entity_id": part.get("id", "unknown"),
                    "entity_type": "Part",
                    "children": [],
                    "properties": part,
                    "impact_count": 1
                })

        hierarchy_node["impact_count"] = len(hierarchy_node["children"])
        return hierarchy_node

    def _count_hierarchy_impacts(self, node: Dict[str, Any]) -> int:
        """Recursively count impacts in hierarchy."""
        count = 1  # Count self
        for child in node.get("children", []):
            count += self._count_hierarchy_impacts(child)
        return count

    def _assess_severity(self, total_impact_count: int) -> str:
        """
        Assess severity based on impact count.

        Args:
            total_impact_count: Total number of affected entities

        Returns:
            Severity level for Camunda decision
        """
        if total_impact_count == 0:
            return "low"
        elif total_impact_count <= 10:
            return "medium"
        elif total_impact_count <= 30:
            return "high"
        else:
            return "critical"

    def _requires_approval(self, severity: str, total_impact_count: int) -> bool:
        """
        Determine if approval is required based on impact.

        Args:
            severity: Impact severity
            total_impact_count: Total affected entities

        Returns:
            True if approval required
        """
        return severity in ["high", "critical"] or total_impact_count > 15
