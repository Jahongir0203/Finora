"""Ilova sozlamalari. Barcha secretlar muhit o'zgaruvchilaridan (Vault/KMS orqali) keladi."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class SmsProvider(StrEnum):
    CONSOLE = "console"  # faqat dev
    ESKIZ = "eskiz"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FINORA_", extra="ignore")

    env: Environment = Environment.DEV
    app_name: str = "Finora API"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://finora_app:finora@localhost:5432/finora"
    redis_url: str | None = "redis://localhost:6379/0"

    # --- SMS (Eskiz.uz). Matn shabloni Eskiz kabinetida oldindan tasdiqlangan bo'lishi kerak
    sms_provider: SmsProvider = SmsProvider.CONSOLE
    eskiz_base_url: str = "https://notify.eskiz.uz/api"
    eskiz_email: str | None = None
    eskiz_password: SecretStr | None = None
    eskiz_sender: str = "4546"
    sms_timeout_seconds: float = 10.0

    # --- Push. Kamida bittasi prod'da majburiy ("New sign-in" bildirishnomasi, 2-bo'lim)
    fcm_service_account_json: SecretStr | None = None
    apns_team_id: str | None = None
    apns_key_id: str | None = None
    apns_private_key: SecretStr | None = None
    apns_bundle_id: str | None = None
    apns_sandbox: bool = False

    # --- Kriptografiya kalitlari (prod'da KMS/Vault'dan) ---
    # ES256 private key (PEM). Dev/test'da bo'sh bo'lsa vaqtinchalik kalit yaratiladi.
    jwt_private_key: SecretStr | None = None
    jwt_issuer: str = "finora"
    # OTP HMAC kaliti, telefon blind-index kaliti, telefonni shifrlash kaliti (32 bayt, base64)
    otp_hmac_key: SecretStr = SecretStr("dev-otp-hmac-key-change-me-0000000")
    blind_index_key: SecretStr = SecretStr("dev-blind-index-key-change-me-000")
    field_encryption_key: SecretStr = SecretStr("ZGV2LWZpZWxkLWtleS0zMi1ieXRlcy1sb25nLSEhISE=")
    refresh_token_pepper: SecretStr = SecretStr("dev-refresh-pepper-change-me-0000")
    # Chek rasmlari uchun imzolangan URL kaliti (02-backend.md, 6-bo'lim)
    url_signing_key: SecretStr = SecretStr("dev-url-signing-key-change-me-000")

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
    # Decompression bomb himoyasi: 10 MB fayl ichida ham 40 MP'dan katta rasm rad etiladi
    max_image_pixels: int = 40_000_000
    receipt_url_ttl_seconds: int = 5 * 60
    receipts_per_hour: int = 30
    # ClamAV (clamd) — prod'da majburiy. Bo'sh bo'lsa dev'da skan o'tkazib yuboriladi
    clamav_host: str | None = None
    clamav_port: int = 3310

    ai_per_hour: int = 20
    ai_per_day: int = 100
    ai_question_max_length: int = 300
    ai_window_days: int = 30

    # security.txt (RFC 9116) uchun aloqa, masalan "mailto:security@finora.uz"
    security_contact: str | None = None

    enforce_https: bool = True
    # So'rov X-Forwarded-Proto'siga ishonish (faqat ishonchli proxy/gateway ortida)
    trust_forwarded_proto: bool = True
    storage_dir: str = "var/storage"
    # S3-mos yopiq bucket. Berilsa lokal disk o'rniga ishlatiladi (prod'da majburiy)
    s3_bucket: str | None = None
    s3_endpoint_url: str | None = None
    s3_region: str | None = None
    s3_kms_key_id: str | None = None

    # /metrics uchun Bearer token (Prometheus scrape). Bo'sh bo'lsa endpoint o'chiq
    metrics_token: SecretStr | None = None

    docs_enabled: bool = Field(default=False, description="Swagger faqat dev'da")

    @property
    def apns_configured(self) -> bool:
        return bool(self.apns_team_id and self.apns_key_id and self.apns_private_key
                    and self.apns_bundle_id)

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
                    "url_signing_key",
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
            if self.sms_provider is SmsProvider.CONSOLE:
                raise ValueError("Prod muhitida real SMS provayderi majburiy (FINORA_SMS_PROVIDER)")
            if not self.fcm_service_account_json and not self.apns_configured:
                raise ValueError("Prod muhitida push provayderi (FCM yoki APNs) majburiy")
            if not self.s3_bucket:
                raise ValueError("Prod muhitida FINORA_S3_BUCKET majburiy (lokal disk emas)")
            if not self.clamav_host:
                raise ValueError("Prod muhitida FINORA_CLAMAV_HOST majburiy (chek antivirus skani)")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
