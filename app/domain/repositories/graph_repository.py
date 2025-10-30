"""
Graph repository interface for engineering graph data.
Follows SOLID principles - Interface Segregation Principle.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities import Line, ISO
from app.domain.repositories.base import IRepository


class IGraphRepository(ABC):
    """
    Interface for graph-based data operations.

    This interface defines operations specific to the engineering graph
    database (Neo4j) without coupling the domain layer to infrastructure.
    """

    @abstractmethod
    async def get_line_by_id(self, line_id: str) -> Optional[Line]:
        """
        Retrieve a Line entity by its ID.

        Args:
            line_id: Unique line identifier

        Returns:
            Line entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_affected_isos_by_line(self, line_id: str) -> List[ISO]:
        """
        Get all ISO drawings affected by a specific line.

        This follows the HAS_ISO relationship in the graph.

        Args:
            line_id: Line identifier

        Returns:
            List of affected ISO entities
        """
        pass

    @abstractmethod
    async def get_affected_spools_by_iso(self, iso_id: str) -> List[dict]:
        """
        Get all fabrication spools affected by an ISO change.

        This follows the FABRICATED_AS relationship in the graph.

        Args:
            iso_id: ISO identifier

        Returns:
            List of affected spool data
        """
        pass

    @abstractmethod
    async def get_affected_parts_by_iso(self, iso_id: str) -> List[dict]:
        """
        Get all parts affected by an ISO change.

        This follows the HAS_PART relationship in the graph.

        Args:
            iso_id: ISO identifier

        Returns:
            List of affected parts data
        """
        pass

    @abstractmethod
    async def traverse_impact_graph(
        self,
        start_entity_type: str,
        start_entity_id: str,
        max_depth: int = 5
    ) -> dict:
        """
        Traverse the graph to find all impacted entities.

        Generic graph traversal for any starting point.

        Args:
            start_entity_type: Type of starting entity (Line, ISO, etc.)
            start_entity_id: ID of starting entity
            max_depth: Maximum depth for traversal

        Returns:
            Dictionary containing all affected entities by type
        """
        pass

    @abstractmethod
    async def get_line_iso_relationship_count(self, line_id: str) -> int:
        """
        Get count of ISOs related to a line.

        Args:
            line_id: Line identifier

        Returns:
            Count of related ISOs
        """
        pass

    @abstractmethod
    async def check_connection(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def close(self):
        """Close database connection and cleanup resources."""
        pass
