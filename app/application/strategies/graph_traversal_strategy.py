"""
Graph traversal strategy for impact analysis.
Uses Neo4j graph queries to find affected entities.
"""
from typing import List
from app.application.strategies.base_strategy import ImpactAnalysisStrategy
from app.domain.entities import ChangeEvent, ImpactResult, ChangeSeverity, ISO
from app.domain.repositories import IGraphRepository
from app.core.logging import log
from app.core.exceptions import EntityNotFoundError, InvalidChangeEventError


class GraphTraversalStrategy(ImpactAnalysisStrategy):
    """
    Strategy that uses graph traversal to analyze impact.

    This is the default strategy for current implementation.
    It queries the Neo4j graph to find all affected entities.
    """

    def __init__(self, graph_repository: IGraphRepository):
        """
        Initialize strategy with graph repository.

        Args:
            graph_repository: Repository for graph operations
        """
        self.graph_repo = graph_repository

    async def analyze(self, change_event: ChangeEvent) -> ImpactResult:
        """
        Analyze impact using graph traversal.

        Args:
            change_event: The change event to analyze

        Returns:
            ImpactResult with affected entities

        Raises:
            InvalidChangeEventError: If change event is invalid
            EntityNotFoundError: If entity doesn't exist
        """
        log.info(f"Analyzing impact for {change_event.entity_type}:{change_event.entity_id}")

        # Validate change event
        if not change_event.entity_id or not change_event.entity_type:
            raise InvalidChangeEventError(
                "Change event must have entity_id and entity_type",
                {"event": change_event.dict()}
            )

        # Create result object
        result = ImpactResult(
            event_id=change_event.event_id,
            analysis_method="graph_traversal"
        )

        # Analyze based on entity type
        if change_event.entity_type.lower() == "line":
            await self._analyze_line_impact(change_event.entity_id, result)
        elif change_event.entity_type.lower() == "iso":
            await self._analyze_iso_impact(change_event.entity_id, result)
        else:
            # Generic graph traversal for other types
            await self._analyze_generic_impact(
                change_event.entity_type,
                change_event.entity_id,
                result
            )

        # Update impact count
        result.update_impact_count()

        # Assess severity based on impact count
        result.severity = self._assess_severity(result.impact_count)

        log.info(f"Impact analysis complete: {result.impact_count} entities affected")
        return result

    async def _analyze_line_impact(self, line_id: str, result: ImpactResult):
        """
        Analyze impact of a Line change.

        Args:
            line_id: Line identifier
            result: Result object to populate
        """
        # Check if line exists
        line = await self.graph_repo.get_line_by_id(line_id)
        if not line:
            raise EntityNotFoundError(
                f"Line not found: {line_id}",
                {"line_id": line_id}
            )

        # Get affected ISOs
        affected_isos = await self.graph_repo.get_affected_isos_by_line(line_id)
        result.affected_isos = affected_isos

        # For each ISO, get affected spools and parts (future extension)
        for iso in affected_isos:
            spools = await self.graph_repo.get_affected_spools_by_iso(iso.id)
            parts = await self.graph_repo.get_affected_parts_by_iso(iso.id)

            result.affected_spools.extend(spools)
            result.affected_parts.extend(parts)

        result.additional_info = {
            "line_id": line_id,
            "total_isos": len(affected_isos),
            "total_spools": len(result.affected_spools),
            "total_parts": len(result.affected_parts)
        }

    async def _analyze_iso_impact(self, iso_id: str, result: ImpactResult):
        """
        Analyze impact of an ISO change.

        Args:
            iso_id: ISO identifier
            result: Result object to populate
        """
        # Get affected spools and parts
        spools = await self.graph_repo.get_affected_spools_by_iso(iso_id)
        parts = await self.graph_repo.get_affected_parts_by_iso(iso_id)

        result.affected_isos = [ISO(**ISO.parse_iso_id(iso_id))]
        result.affected_spools = spools
        result.affected_parts = parts

        result.additional_info = {
            "iso_id": iso_id,
            "total_spools": len(spools),
            "total_parts": len(parts)
        }

    async def _analyze_generic_impact(
        self,
        entity_type: str,
        entity_id: str,
        result: ImpactResult
    ):
        """
        Generic impact analysis using graph traversal.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            result: Result object to populate
        """
        affected_entities = await self.graph_repo.traverse_impact_graph(
            entity_type,
            entity_id,
            max_depth=5
        )

        # Populate result based on affected entities
        if "ISO" in affected_entities:
            result.affected_isos = [
                ISO(**ISO.parse_iso_id(iso["id"]))
                for iso in affected_entities["ISO"]
            ]

        if "SPOOL" in affected_entities:
            result.affected_spools = affected_entities["SPOOL"]

        if "Part" in affected_entities:
            result.affected_parts = affected_entities["Part"]

        result.additional_info = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "affected_entity_types": list(affected_entities.keys())
        }

    def _assess_severity(self, impact_count: int) -> ChangeSeverity:
        """
        Assess severity based on impact count.

        Args:
            impact_count: Number of affected entities

        Returns:
            ChangeSeverity level
        """
        if impact_count == 0:
            return ChangeSeverity.LOW
        elif impact_count <= 5:
            return ChangeSeverity.MEDIUM
        elif impact_count <= 15:
            return ChangeSeverity.HIGH
        else:
            return ChangeSeverity.CRITICAL

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "graph_traversal"

    def supports_entity_type(self, entity_type: str) -> bool:
        """Check if entity type is supported."""
        supported_types = ["line", "iso", "equipment", "spool", "part"]
        return entity_type.lower() in supported_types
