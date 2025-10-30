"""
Neo4j database client.
Handles connection management and session lifecycle.
Follows SOLID - Single Responsibility for connection management.
"""
from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import Optional
from app.core.config import settings
from app.core.logging import log
from app.core.exceptions import DatabaseConnectionError


class Neo4jClient:
    """
    Neo4j database client with connection pooling.

    Manages the lifecycle of Neo4j driver and provides session management.
    Implements Singleton pattern for database connection.
    """

    _instance: Optional['Neo4jClient'] = None
    _driver: Optional[AsyncDriver] = None

    def __new__(cls):
        """Singleton implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> AsyncDriver:
        """
        Establish connection to Neo4j database.

        Returns:
            AsyncDriver instance

        Raises:
            DatabaseConnectionError: If connection fails
        """
        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                    max_connection_lifetime=settings.neo4j_max_connection_lifetime,
                    max_connection_pool_size=settings.neo4j_max_connection_pool_size,
                    connection_acquisition_timeout=settings.neo4j_connection_acquisition_timeout
                )

                # Verify connectivity
                await self._driver.verify_connectivity()
                log.info(f"Connected to Neo4j at {settings.neo4j_uri}")

            except Exception as e:
                log.error(f"Failed to connect to Neo4j: {str(e)}")
                raise DatabaseConnectionError(
                    f"Neo4j connection failed: {str(e)}",
                    {"uri": settings.neo4j_uri}
                )

        return self._driver

    async def close(self):
        """Close Neo4j driver connection."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            log.info("Neo4j connection closed")

    async def verify_connectivity(self) -> bool:
        """
        Verify database connection is healthy.

        Returns:
            True if connected, False otherwise
        """
        try:
            if self._driver is None:
                await self.connect()

            await self._driver.verify_connectivity()
            return True
        except Exception as e:
            log.error(f"Connectivity check failed: {str(e)}")
            return False

    def get_driver(self) -> Optional[AsyncDriver]:
        """Get the current driver instance."""
        return self._driver

    async def execute_query(self, query: str, parameters: dict = None, database: str = None):
        """
        Execute a Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name (default from settings)

        Returns:
            Query result

        Raises:
            DatabaseConnectionError: If query execution fails
        """
        if self._driver is None:
            await self.connect()

        db = database or settings.neo4j_database

        try:
            result = await self._driver.execute_query(
                query,
                parameters or {},
                database_=db
            )
            return result
        except Exception as e:
            log.error(f"Query execution failed: {str(e)}")
            raise DatabaseConnectionError(
                f"Query execution error: {str(e)}",
                {"query": query, "parameters": parameters}
            )


# Singleton instance
neo4j_client = Neo4jClient()
