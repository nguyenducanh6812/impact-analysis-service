"""
Neo4j repository implementation.
Concrete implementation of IGraphRepository interface.
Follows SOLID - Dependency Inversion Principle.
"""
from typing import List, Optional
from app.domain.repositories.graph_repository import IGraphRepository
from app.domain.entities import Line, ISO
from app.infrastructure.database.neo4j_client import neo4j_client
from app.core.logging import log
from app.core.exceptions import EntityNotFoundError, DatabaseConnectionError


class Neo4jGraphRepository(IGraphRepository):
    """
    Neo4j implementation of graph repository.

    Handles all graph database operations for engineering data.
    """

    def __init__(self):
        """Initialize repository with Neo4j client."""
        self.client = neo4j_client

    async def get_line_by_id(self, line_id: str) -> Optional[Line]:
        """
        Retrieve a Line entity by its ID.

        Args:
            line_id: Unique line identifier

        Returns:
            Line entity if found, None otherwise
        """
        query = """
        MATCH (l:Line {id: $line_id})
        RETURN l
        """

        try:
            result = await self.client.execute_query(
                query,
                {"line_id": line_id}
            )

            if result.records:
                node = result.records[0]["l"]
                return Line(**dict(node))

            return None

        except Exception as e:
            log.error(f"Error fetching line {line_id}: {str(e)}")
            raise DatabaseConnectionError(
                f"Failed to fetch line: {str(e)}",
                {"line_id": line_id}
            )

    async def get_affected_isos_by_line(self, line_id: str) -> List[ISO]:
        """
        Get all ISO drawings affected by a specific line.

        Args:
            line_id: Line identifier

        Returns:
            List of affected ISO entities
        """
        query = """
        MATCH (l:Line {id: $line_id})-[:HAS_ISO]->(i:ISO)
        RETURN i
        ORDER BY i.id
        """

        try:
            result = await self.client.execute_query(
                query,
                {"line_id": line_id}
            )

            isos = []
            for record in result.records:
                iso_node = record["i"]
                iso_data = ISO.parse_iso_id(iso_node["id"])
                isos.append(ISO(**iso_data))

            log.info(f"Found {len(isos)} ISOs affected by line {line_id}")
            return isos

        except Exception as e:
            log.error(f"Error fetching affected ISOs for line {line_id}: {str(e)}")
            raise DatabaseConnectionError(
                f"Failed to fetch affected ISOs: {str(e)}",
                {"line_id": line_id}
            )

    async def get_affected_spools_by_iso(self, iso_id: str) -> List[dict]:
        """
        Get all fabrication spools affected by an ISO change.

        Args:
            iso_id: ISO identifier

        Returns:
            List of affected spool data
        """
        query = """
        MATCH (i:ISO {id: $iso_id})-[:FABRICATED_AS]->(s:SPOOL)
        RETURN s
        ORDER BY s.id
        """

        try:
            result = await self.client.execute_query(
                query,
                {"iso_id": iso_id}
            )

            spools = [dict(record["s"]) for record in result.records]
            log.info(f"Found {len(spools)} spools affected by ISO {iso_id}")
            return spools

        except Exception as e:
            log.error(f"Error fetching affected spools for ISO {iso_id}: {str(e)}")
            raise DatabaseConnectionError(
                f"Failed to fetch affected spools: {str(e)}",
                {"iso_id": iso_id}
            )

    async def get_affected_parts_by_iso(self, iso_id: str) -> List[dict]:
        """
        Get all parts affected by an ISO change.

        Args:
            iso_id: ISO identifier

        Returns:
            List of affected parts data
        """
        query = """
        MATCH (i:ISO {id: $iso_id})-[:HAS_PART]->(p:Part)
        RETURN p
        ORDER BY p.id
        """

        try:
            result = await self.client.execute_query(
                query,
                {"iso_id": iso_id}
            )

            parts = [dict(record["p"]) for record in result.records]
            log.info(f"Found {len(parts)} parts affected by ISO {iso_id}")
            return parts

        except Exception as e:
            log.error(f"Error fetching affected parts for ISO {iso_id}: {str(e)}")
            raise DatabaseConnectionError(
                f"Failed to fetch affected parts: {str(e)}",
                {"iso_id": iso_id}
            )

    async def traverse_impact_graph(
        self,
        start_entity_type: str,
        start_entity_id: str,
        max_depth: int = 5
    ) -> dict:
        """
        Traverse the graph to find all impacted entities.

        Args:
            start_entity_type: Type of starting entity
            start_entity_id: ID of starting entity
            max_depth: Maximum depth for traversal

        Returns:
            Dictionary containing all affected entities by type
        """
        query = f"""
        MATCH path = (start:{start_entity_type} {{id: $entity_id}})-[*1..{max_depth}]->(affected)
        RETURN DISTINCT labels(affected) as labels, affected
        """

        try:
            result = await self.client.execute_query(
                query,
                {"entity_id": start_entity_id}
            )

            affected_entities = {}
            for record in result.records:
                label = record["labels"][0] if record["labels"] else "Unknown"
                entity = dict(record["affected"])

                if label not in affected_entities:
                    affected_entities[label] = []

                affected_entities[label].append(entity)

            log.info(f"Graph traversal found {len(affected_entities)} entity types affected")
            return affected_entities

        except Exception as e:
            log.error(f"Error traversing impact graph: {str(e)}")
            raise DatabaseConnectionError(
                f"Failed to traverse impact graph: {str(e)}",
                {"start_entity": start_entity_id}
            )

    async def get_line_iso_relationship_count(self, line_id: str) -> int:
        """
        Get count of ISOs related to a line.

        Args:
            line_id: Line identifier

        Returns:
            Count of related ISOs
        """
        query = """
        MATCH (l:Line {id: $line_id})-[:HAS_ISO]->(i:ISO)
        RETURN count(i) as iso_count
        """

        try:
            result = await self.client.execute_query(
                query,
                {"line_id": line_id}
            )

            if result.records:
                return result.records[0]["iso_count"]

            return 0

        except Exception as e:
            log.error(f"Error counting ISOs for line {line_id}: {str(e)}")
            raise DatabaseConnectionError(
                f"Failed to count ISOs: {str(e)}",
                {"line_id": line_id}
            )

    async def check_connection(self) -> bool:
        """Check if database connection is healthy."""
        return await self.client.verify_connectivity()

    async def close(self):
        """Close database connection."""
        await self.client.close()
