"""
Base repository interface.
Follows SOLID principles - Interface Segregation and Dependency Inversion.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """
    Base repository interface following Repository pattern.

    This abstract class defines the contract for all repositories.
    Concrete implementations will handle specific data sources (Neo4j, SQL, etc.)
    """

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        Retrieve all entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists.

        Args:
            entity_id: Unique identifier of the entity

        Returns:
            True if exists, False otherwise
        """
        pass
