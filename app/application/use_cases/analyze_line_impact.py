"""
Analyze Line Impact Use Case.
Orchestrates the impact analysis for line changes.
Follows Clean Architecture - Use Case layer.
"""
from app.domain.entities import ChangeEvent, ImpactResult
from app.application.strategies import ImpactAnalysisStrategy
from app.core.logging import log
from app.core.exceptions import InvalidChangeEventError


class AnalyzeLineImpactUseCase:
    """
    Use case for analyzing the impact of line changes.

    This class orchestrates the business logic for impact analysis,
    delegating to the appropriate strategy pattern implementation.
    """

    def __init__(self, strategy: ImpactAnalysisStrategy):
        """
        Initialize use case with analysis strategy.

        Args:
            strategy: Impact analysis strategy to use
        """
        self.strategy = strategy

    async def execute(self, change_event: ChangeEvent) -> ImpactResult:
        """
        Execute the impact analysis use case.

        Args:
            change_event: The change event to analyze

        Returns:
            ImpactResult containing analysis results

        Raises:
            InvalidChangeEventError: If change event is invalid
            EntityNotFoundError: If entity doesn't exist
        """
        log.info(f"Executing analyze impact use case for event: {change_event.event_id}")

        # Validate change event
        self._validate_change_event(change_event)

        # Check if strategy supports this entity type
        if not self.strategy.supports_entity_type(change_event.entity_type):
            raise InvalidChangeEventError(
                f"Strategy '{self.strategy.get_strategy_name()}' does not support entity type '{change_event.entity_type}'",
                {"entity_type": change_event.entity_type, "strategy": self.strategy.get_strategy_name()}
            )

        # Execute analysis using strategy
        result = await self.strategy.analyze(change_event)

        log.info(f"Impact analysis completed: {result.impact_count} entities affected, severity: {result.severity}")

        return result

    def _validate_change_event(self, change_event: ChangeEvent):
        """
        Validate change event data.

        Args:
            change_event: Change event to validate

        Raises:
            InvalidChangeEventError: If validation fails
        """
        if not change_event.entity_id:
            raise InvalidChangeEventError(
                "entity_id is required",
                {"change_event": change_event.dict()}
            )

        if not change_event.entity_type:
            raise InvalidChangeEventError(
                "entity_type is required",
                {"change_event": change_event.dict()}
            )

        if not change_event.description:
            raise InvalidChangeEventError(
                "description is required",
                {"change_event": change_event.dict()}
            )

        log.debug(f"Change event validation passed for {change_event.event_id}")
