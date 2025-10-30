"""
Dependency injection for FastAPI.
Follows SOLID - Dependency Inversion Principle.
"""
from typing import AsyncGenerator
from fastapi import Depends
from app.infrastructure.database import Neo4jGraphRepository, neo4j_client
from app.application.strategies import GraphTraversalStrategy, SimulationStrategy
from app.application.use_cases import AnalyzeLineImpactUseCase
from app.domain.repositories import IGraphRepository
from app.core.logging import log


# Repository dependencies
async def get_graph_repository() -> AsyncGenerator[IGraphRepository, None]:
    """
    Get graph repository instance.

    Yields:
        IGraphRepository implementation

    Note: Using dependency injection allows easy swapping of implementations
    """
    # Ensure connection
    await neo4j_client.connect()

    # Create repository instance
    repo = Neo4jGraphRepository()

    try:
        yield repo
    finally:
        # Cleanup is handled by the client singleton
        pass


# Strategy dependencies
async def get_graph_traversal_strategy(
    graph_repo: IGraphRepository = Depends(get_graph_repository)
) -> GraphTraversalStrategy:
    """
    Get graph traversal strategy instance.

    Args:
        graph_repo: Injected graph repository

    Returns:
        GraphTraversalStrategy instance
    """
    return GraphTraversalStrategy(graph_repo)


async def get_simulation_strategy(
    graph_repo: IGraphRepository = Depends(get_graph_repository)
) -> SimulationStrategy:
    """
    Get simulation strategy instance (future implementation).

    Args:
        graph_repo: Injected graph repository

    Returns:
        SimulationStrategy instance
    """
    return SimulationStrategy(graph_repo)


# Use case dependencies
async def get_analyze_impact_use_case(
    strategy: GraphTraversalStrategy = Depends(get_graph_traversal_strategy)
) -> AnalyzeLineImpactUseCase:
    """
    Get analyze impact use case with graph traversal strategy.

    Args:
        strategy: Injected analysis strategy

    Returns:
        AnalyzeLineImpactUseCase instance
    """
    return AnalyzeLineImpactUseCase(strategy)


async def get_analyze_impact_use_case_with_simulation(
    strategy: SimulationStrategy = Depends(get_simulation_strategy)
) -> AnalyzeLineImpactUseCase:
    """
    Get analyze impact use case with simulation strategy.

    Args:
        strategy: Injected simulation strategy

    Returns:
        AnalyzeLineImpactUseCase instance
    """
    return AnalyzeLineImpactUseCase(strategy)
