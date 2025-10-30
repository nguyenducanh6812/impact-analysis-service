"""
Base strategy for impact analysis.
Follows SOLID - Strategy Pattern (Open/Closed Principle).
"""
from abc import ABC, abstractmethod
from app.domain.entities import ChangeEvent, ImpactResult


class ImpactAnalysisStrategy(ABC):
    """
    Abstract base class for impact analysis strategies.

    This allows different analysis methods (graph traversal, simulation, etc.)
    to be swapped without changing client code.
    """

    @abstractmethod
    async def analyze(self, change_event: ChangeEvent) -> ImpactResult:
        """
        Analyze the impact of a change event.

        Args:
            change_event: The change event to analyze

        Returns:
            ImpactResult containing analysis results

        Raises:
            InvalidChangeEventError: If change event is invalid
            DatabaseConnectionError: If database operation fails
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy.

        Returns:
            Strategy name (e.g., "graph_traversal", "simulation")
        """
        pass

    @abstractmethod
    def supports_entity_type(self, entity_type: str) -> bool:
        """
        Check if this strategy supports the given entity type.

        Args:
            entity_type: Type of entity (Line, ISO, etc.)

        Returns:
            True if supported, False otherwise
        """
        pass
