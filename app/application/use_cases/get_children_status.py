"""
Get Children Status Use Case.
Generic - works for any entity type (LINE, ISO, SPOOL).
Returns hierarchical tree with id, type, status, and recursive children.
"""
from typing import List, Dict, Any
from app.domain.repositories import IGraphRepository
from app.core.logging import log


class GetChildrenStatusUseCase:
    """
    Use case for getting children of any entity in hierarchical tree structure.

    Returns id, type, status, and recursive children.
    Works for LINE, ISO, SPOOL, or any other entity type.
    """

    def __init__(self, graph_repository: IGraphRepository):
        """Initialize with graph repository."""
        self.graph_repo = graph_repository

    async def execute(self, entity_id: str) -> Dict[str, Any]:
        """
        Get children for any entity in hierarchical tree structure.

        This query finds all children recursively:
        - LINE → ISOs
        - ISO → SPOOLs (with their Parts nested inside)
        - SPOOL → Parts

        Args:
            entity_id: Entity identifier

        Returns:
            Dictionary with entity_id, entity_type, and hierarchical children tree
        """
        log.info(f"Getting hierarchical children for entity: {entity_id}")

        try:
            # First, get the entity itself to determine its type
            entity_result = await self.graph_repo.client.execute_query(
                """
                MATCH (entity {id: $entity_id})
                RETURN entity, labels(entity) as entity_labels
                """,
                {"entity_id": entity_id}
            )

            if not entity_result.records:
                log.warning(f"Entity not found: {entity_id}")
                return {
                    "entity_id": entity_id,
                    "entity_type": "Unknown",
                    "children": []
                }

            entity_record = entity_result.records[0]
            entity_labels = entity_record["entity_labels"]
            entity_type = entity_labels[0] if entity_labels else "Unknown"

            # Build hierarchical tree recursively
            children = await self._get_children_recursive(entity_id)

            log.info(f"Found {len(children)} top-level children for entity {entity_id}")

            return {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "children": children
            }

        except Exception as e:
            log.error(f"Error getting children for entity {entity_id}: {str(e)}")
            # Return empty children list on error
            return {
                "entity_id": entity_id,
                "entity_type": "Unknown",
                "children": []
            }

    async def _get_children_recursive(self, parent_id: str) -> List[Dict[str, Any]]:
        """
        Recursively get children and their descendants.

        Args:
            parent_id: Parent entity ID

        Returns:
            List of child nodes with their recursive children
        """
        # Query: Get direct children with their labels
        result = await self.graph_repo.client.execute_query(
            """
            MATCH (parent {id: $parent_id})-[r]->(child)
            RETURN child, labels(child) as child_labels
            ORDER BY child.id
            """,
            {"parent_id": parent_id}
        )

        children = []
        for record in result.records:
            child = dict(record["child"])
            child_labels = record["child_labels"]
            child_type = child_labels[0] if child_labels else "Unknown"
            child_id = child.get("id", "unknown")

            # Recursively get children of this child
            grandchildren = await self._get_children_recursive(child_id)

            # Build child node
            child_node = {
                "id": child_id,
                "type": child_type,
                "status": child.get("latest_status") or child.get("status"),
                "children": grandchildren
            }
            children.append(child_node)

        return children
