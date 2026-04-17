import secrets
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NkFinOps - Chargeback Automation"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str = ""  # REQUIRED — must be set via env or .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/finops_chargeback"
    DATABASE_SYNC_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/finops_chargeback"

    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_CUR_S3_BUCKET: Optional[str] = None
    AWS_CUR_S3_PREFIX: Optional[str] = None

    # MongoDB Atlas
    MONGODB_ATLAS_PUBLIC_KEY: Optional[str] = None
    MONGODB_ATLAS_PRIVATE_KEY: Optional[str] = None
    MONGODB_ATLAS_ORG_ID: Optional[str] = None

    # Datadog
    DATADOG_API_KEY: Optional[str] = None
    DATADOG_APP_KEY: Optional[str] = None
    DATADOG_SITE: str = "datadoghq.com"

    # Confluent
    CONFLUENT_API_KEY: Optional[str] = None
    CONFLUENT_API_SECRET: Optional[str] = None

    # SingleStore
    SINGLESTORE_API_KEY: Optional[str] = None

    # Harness
    HARNESS_API_TOKEN: Optional[str] = None
    HARNESS_ACCOUNT_ID: Optional[str] = None

    # Management Fee
    MANAGEMENT_FEE_RATE: float = 0.20

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if not v or v in ("", "CHANGE-ME-IN-PRODUCTION"):
            raise ValueError(
                "SECRET_KEY must be explicitly set in environment or .env file. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
