"""
Custom exceptions for the Impact Analysis Service.
Follows SOLID principles - clearly defined exception hierarchy.
"""


class ImpactAnalysisException(Exception):
    """Base exception for all impact analysis errors."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionError(ImpactAnalysisException):
    """Raised when database connection fails."""
    pass


class EntityNotFoundError(ImpactAnalysisException):
    """Raised when a requested entity is not found."""
    pass


class InvalidChangeEventError(ImpactAnalysisException):
    """Raised when a change event is invalid."""
    pass


class SimulationError(ImpactAnalysisException):
    """Raised when simulation execution fails."""
    pass


class ConfigurationError(ImpactAnalysisException):
    """Raised when configuration is invalid."""
    pass
