"""Domen xatolari. HTTP'ni bilmaydi — status kodlariga presentation qatlami moslaydi."""


class DomainError(Exception):
    code: str = "domain_error"
    message: str = "Xatolik yuz berdi"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        self.message = message or self.message


class NotFoundError(DomainError):
    """Resurs yo'q YOKI boshqa userniki — ikkalasi bir xil ko'rinadi (BOLA/IDOR himoyasi)."""

    code = "not_found"
    message = "Resurs topilmadi"


class ValidationFailedError(DomainError):
    code = "validation_error"
    message = "Ma'lumot noto'g'ri"


class InsufficientFundsError(DomainError):
    code = "insufficient_funds"
    message = "Yechish summasi jamg'armadan oshib ketdi"


class RateLimitedError(DomainError):
    code = "rate_limited"
    message = "Juda ko'p so'rov. Keyinroq urinib ko'ring"

    def __init__(self, retry_after: int, message: str | None = None) -> None:
        super().__init__(message)
        self.retry_after = max(1, int(retry_after))


class OtpBlockedError(RateLimitedError):
    code = "otp_blocked"
    message = "Juda ko'p noto'g'ri urinish. Raqam vaqtincha bloklandi"


class InvalidOtpError(DomainError):
    code = "invalid_code"
    message = "Kod noto'g'ri yoki muddati o'tgan"


class AuthenticationError(DomainError):
    code = "unauthorized"
    message = "Avtorizatsiya talab qilinadi"


class InvalidDeviceSignatureError(AuthenticationError):
    code = "invalid_device_signature"
    message = "Qurilma imzosi noto'g'ri"


class TokenReuseDetectedError(AuthenticationError):
    code = "session_revoked"
    message = "Sessiya bekor qilindi. Qayta kiring"


class ServiceUnavailableError(DomainError):
    """Tashqi xizmat (SMS provayderi va h.k.) ishlamayapti. Tafsilot mijozga aytilmaydi."""

    code = "service_unavailable"
    message = "Xizmat vaqtincha ishlamayapti. Keyinroq urinib ko'ring"


class ConflictError(DomainError):
    code = "conflict"
    message = "Bunday yozuv allaqachon mavjud"


class UnsupportedMediaError(DomainError):
    code = "unsupported_media_type"
    message = "Faqat JPEG, PNG yoki HEIC rasm qabul qilinadi"


class FileRejectedError(DomainError):
    """Antivirus yoki rasm tekshiruvidan o'tmagan fayl. Sabab mijozga aytilmaydi."""

    code = "file_rejected"
    message = "Fayl qabul qilinmadi"


class IdempotencyKeyRequiredError(DomainError):
    code = "idempotency_key_required"
    message = "Idempotency-Key sarlavhasi majburiy"


class IdempotencyConflictError(DomainError):
    code = "idempotency_conflict"
    message = "Bu Idempotency-Key boshqa so'rov bilan ishlatilgan"
