"""
Configuration management for the Impact Analysis Service.
Follows SOLID principles - Single Responsibility for configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Impact Analysis Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"
    api_v2_prefix: str = "/api/v2"

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "12345678"
    neo4j_database: str = "so17113"
    neo4j_max_connection_lifetime: int = 3600
    neo4j_max_connection_pool_size: int = 50
    neo4j_connection_acquisition_timeout: int = 60

    # Simulation Settings (for future DES)
    simulation_enabled: bool = False
    simulation_default_duration: int = 100
    simulation_resource_capacity: int = 5

    # Logging
    log_level: str = "INFO"
    log_format: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Singleton instance
settings = Settings()
