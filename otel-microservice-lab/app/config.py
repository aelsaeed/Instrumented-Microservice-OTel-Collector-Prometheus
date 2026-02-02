from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OTEL_LAB_", case_sensitive=False)

    service_name: str = "otel-microservice-lab"
    environment: str = "local"
    database_url: str = "postgresql+psycopg://postgres:postgres@postgres:5432/items"
    redis_url: str = "redis://redis:6379/0"
    cache_ttl_seconds: int = 30
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4317"
    otel_exporter_otlp_protocol: str = "grpc"
    otel_log_level: str = "INFO"
    log_json: bool = True


settings = Settings()
