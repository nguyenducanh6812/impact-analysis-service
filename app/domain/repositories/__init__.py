"""Domain repository interfaces."""
from app.domain.repositories.base import IRepository
from app.domain.repositories.graph_repository import IGraphRepository

__all__ = ["IRepository", "IGraphRepository"]
