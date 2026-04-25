from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Asset Management API"
    environment: str = "dev"
    schema_version: str = "1.0.0"
    policy_version: str = "1.0.0"
    app_version: str = "0.1.0"
    dynamodb_mode: str = "local"
    dynamodb_endpoint_url: str | None = "http://localhost:55000"
    aws_region: str = "us-east-1"
    approvals_table_name: str = "asset-management-dev-approvals"
    audit_events_table_name: str = "asset-management-dev-audit-events"
    portfolios_table_name: str = "asset-management-dev-portfolios"
    sessions_table_name: str = "asset-management-dev-sessions"
    memory_queue_table_name: str = "asset-management-dev-memory-queue"
    research_agent_url: str = "http://localhost:8101/a2a/research"
    research_agent_remote_enabled: bool = True
    sentiment_mcp_url: str = "http://localhost:8201/mcp"
    sentiment_mcp_enabled: bool = True
    remote_agent_timeout_seconds: float = 2.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
