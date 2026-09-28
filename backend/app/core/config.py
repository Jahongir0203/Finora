"""Ilova sozlamalari. Barcha secretlar muhit o'zgaruvchilaridan (Vault/KMS orqali) keladi."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FINORA_", extra="ignore")

    env: Environment = Environment.DEV
    app_name: str = "Finora API"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://finora_app:finora@localhost:5432/finora"
    redis_url: str | None = "redis://localhost:6379/0"

    # --- Kriptografiya kalitlari (prod'da KMS/Vault'dan) ---
    # ES256 private key (PEM). Dev/test'da bo'sh bo'lsa vaqtinchalik kalit yaratiladi.
    jwt_private_key: SecretStr | None = None
    jwt_issuer: str = "finora"
    # OTP HMAC kaliti, telefon blind-index kaliti, telefonni shifrlash kaliti (32 bayt, base64)
    otp_hmac_key: SecretStr = SecretStr("dev-otp-hmac-key-change-me-0000000")
    blind_index_key: SecretStr = SecretStr("dev-blind-index-key-change-me-000")
    field_encryption_key: SecretStr = SecretStr("ZGV2LWZpZWxkLWtleS0zMi1ieXRlcy1sb25nLSEhISE=")
    refresh_token_pepper: SecretStr = SecretStr("dev-refresh-pepper-change-me-0000")

    # --- 01-umumiy.md, 2-bo'lim: parametrlar jadvali ---
    otp_length: int = 6
    otp_ttl_seconds: int = 120
    otp_resend_seconds: int = 60
    otp_per_hour: int = 5
    otp_per_day: int = 10
    # IP bo'yicha limit yumshoqroq: mobil operatorlar CGNAT ortida ko'p user bitta IP'da
    otp_ip_per_hour: int = 30
    otp_ip_per_day: int = 100
    otp_max_attempts: int = 5
    otp_block_seconds: int = 15 * 60
    otp_verify_per_hour: int = 20

    access_token_ttl_seconds: int = 15 * 60
    refresh_token_ttl_seconds: int = 30 * 24 * 3600
    refresh_per_hour: int = 30
    device_signature_window_seconds: int = 60

    idempotency_ttl_seconds: int = 24 * 3600
    export_ttl_seconds: int = 24 * 3600
    exports_per_hour: int = 10
    default_user_rate_per_minute: int = 300

    max_body_bytes: int = 1 * 1024 * 1024
    max_receipt_bytes: int = 10 * 1024 * 1024

    enforce_https: bool = True
    # So'rov X-Forwarded-Proto'siga ishonish (faqat ishonchli proxy/gateway ortida)
    trust_forwarded_proto: bool = True
    storage_dir: str = "var/storage"

    docs_enabled: bool = Field(default=False, description="Swagger faqat dev'da")

    @model_validator(mode="after")
    def _prod_guards(self) -> "Settings":
        if self.env is Environment.PROD:
            insecure = [
                name
                for name in (
                    "otp_hmac_key",
                    "blind_index_key",
                    "field_encryption_key",
                    "refresh_token_pepper",
                )
                if "dev-" in getattr(self, name).get_secret_value()
                or getattr(self, name).get_secret_value()
                == Settings.model_fields[name].default.get_secret_value()
            ]
            if insecure:
                raise ValueError(f"Prod muhitida standart kalitlar taqiqlangan: {insecure}")
            if self.jwt_private_key is None:
                raise ValueError("Prod muhitida FINORA_JWT_PRIVATE_KEY majburiy")
            if self.docs_enabled:
                raise ValueError("Prod muhitida Swagger o'chirilgan bo'lishi kerak")
            if not self.enforce_https:
                raise ValueError("Prod muhitida HTTPS majburiy")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
