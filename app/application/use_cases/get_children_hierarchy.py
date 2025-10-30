"""
Get Children Hierarchy Use Case.
Returns simplified, recursive hierarchy of affected children.
"""
from typing import List, Dict, Any, Optional
from app.domain.repositories import IGraphRepository
from app.core.logging import log


class GetChildrenHierarchyUseCase:
    """
    Use case for getting hierarchical children structure.

    Returns minimal data: id, latest_status, and recursive children.
    """

    def __init__(self, graph_repository: IGraphRepository):
        """Initialize with graph repository."""
        self.graph_repo = graph_repository

    async def execute(
        self,
        entity_type: str,
        entity_id: str,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        Get children hierarchy for a single entity.

        Args:
            entity_type: Type of entity (Line, ISO, SPOOL)
            entity_id: Entity identifier
            depth: How many levels deep to traverse

        Returns:
            Dictionary with id, children list, and total count
        """
        log.info(f"Getting children for {entity_type}:{entity_id}, depth={depth}")

        if entity_type.lower() == "line":
            children = await self._get_line_children(entity_id, depth, current_depth=1)
        elif entity_type.lower() == "iso":
            children = await self._get_iso_children(entity_id, depth, current_depth=1)
        elif entity_type.lower() == "spool":
            children = await self._get_spool_children(entity_id, depth, current_depth=1)
        else:
            log.warning(f"Unsupported entity type: {entity_type}")
            children = []

        total = self._count_descendants(children)

        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "children": children,
            "total_descendants": total
        }

    async def _get_line_children(
        self,
        line_id: str,
        max_depth: int,
        current_depth: int
    ) -> List[Dict[str, Any]]:
        """Get children for a Line."""
        if current_depth > max_depth:
            return []

        # Line -> ISOs
        isos = await self.graph_repo.get_affected_isos_by_line(line_id)

        children = []
        for iso in isos:
            iso_node = {
                "id": iso.id,
                "latest_status": None,
                "children": []
            }

            # If we can go deeper, get ISO's children
            if current_depth < max_depth:
                iso_node["children"] = await self._get_iso_children(
                    iso.id,
                    max_depth,
                    current_depth + 1
                )

            children.append(iso_node)

        return children

    async def _get_iso_children(
        self,
        iso_id: str,
        max_depth: int,
        current_depth: int
    ) -> List[Dict[str, Any]]:
        """Get children for an ISO."""
        if current_depth > max_depth:
            return []

        children = []

        # ISO -> SPOOLs
        spools = await self.graph_repo.get_affected_spools_by_iso(iso_id)
        for spool in spools:
            spool_node = {
                "id": spool.get("id", "unknown"),
                "latest_status": spool.get("latest_status"),
                "children": []
            }

            # If we can go deeper, get SPOOL's children
            if current_depth < max_depth:
                spool_node["children"] = await self._get_spool_children(
                    spool.get("id", "unknown"),
                    max_depth,
                    current_depth + 1
                )

            children.append(spool_node)

        # ISO -> Parts (direct parts, not in spools)
        parts = await self.graph_repo.get_affected_parts_by_iso(iso_id)
        for part in parts:
            part_node = {
                "id": part.get("id", "unknown"),
                "latest_status": None,  # Parts typically don't have status
                "children": []
            }
            children.append(part_node)

        return children

    async def _get_spool_children(
        self,
        spool_id: str,
        max_depth: int,
        current_depth: int
    ) -> List[Dict[str, Any]]:
        """Get children for a SPOOL (parts grouped in the spool)."""
        if current_depth > max_depth:
            return []

        # SPOOL -> Parts
        # Query: MATCH (s:SPOOL {id: $spool_id})-[:GROUPS]->(p:Part) RETURN p
        try:
            result = await self.graph_repo.client.execute_query(
                """
                MATCH (s:SPOOL {id: $spool_id})-[:GROUPS]->(p:Part)
                RETURN p
                """,
                {"spool_id": spool_id}
            )

            children = []
            for record in result.records:
                part = dict(record["p"])
                part_node = {
                    "id": part.get("id", "unknown"),
                    "latest_status": None,
                    "children": []
                }
                children.append(part_node)

            return children

        except Exception as e:
            log.error(f"Error getting SPOOL children: {str(e)}")
            return []

    def _count_descendants(self, children: List[Dict[str, Any]]) -> int:
        """Recursively count all descendants."""
        count = len(children)
        for child in children:
            count += self._count_descendants(child.get("children", []))
        return count
