"""Domen xatolari. HTTP'ni bilmaydi — status kodlariga presentation qatlami moslaydi."""


class DomainError(Exception):
    code: str = "domain_error"
    message: str = "Xatolik yuz berdi"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        # Aniq (maxsus) xabar berilganmi — lokalizatsiyada umumiy matn bilan almashtirilmaydi
        self.custom_message = message is not None
        self.message = message or self.message

    def extra(self) -> dict[str, object]:
        """Xato javobiga qo'shiladigan maydonlar (fields, attempts_left, ...)."""
        return {}


class NotFoundError(DomainError):
    """Resurs yo'q YOKI boshqa userniki — ikkalasi bir xil ko'rinadi (BOLA/IDOR himoyasi)."""

    code = "not_found"
    message = "Resurs topilmadi"


class ValidationFailedError(DomainError):
    code = "validation_error"
    message = "Ma'lumot noto'g'ri"

    def __init__(self, message: str | None = None, *, fields: list[str] | None = None,
                 code: str | None = None) -> None:
        super().__init__(message)
        self.fields = fields or []
        if code is not None:
            self.code = code

    def extra(self) -> dict[str, object]:
        return {"fields": self.fields}


class InsufficientFundsError(DomainError):
    code = "insufficient_funds"
    message = "Yechish summasi jamg'armadan oshib ketdi"


class RateLimitedError(DomainError):
    code = "rate_limited"
    message = "Juda ko'p so'rov. Keyinroq urinib ko'ring"

    def __init__(self, retry_after: int, message: str | None = None) -> None:
        super().__init__(message)
        self.retry_after = max(1, int(retry_after))

    def extra(self) -> dict[str, object]:
        return {"retry_after": self.retry_after}


class OtpBlockedError(RateLimitedError):
    code = "otp_blocked"
    message = "Juda ko'p noto'g'ri urinish. Raqam vaqtincha bloklandi"


class InvalidOtpError(DomainError):
    code = "otp_invalid"
    message = "Kod noto'g'ri"

    def __init__(self, attempts_left: int | None = None) -> None:
        super().__init__()
        self.attempts_left = attempts_left

    def extra(self) -> dict[str, object]:
        return {} if self.attempts_left is None else {"attempts_left": self.attempts_left}


class OtpExpiredError(InvalidOtpError):
    code = "otp_expired"
    message = "Kod muddati o'tdi. Yangisini so'rang"


class AuthenticationError(DomainError):
    code = "unauthorized"
    message = "Avtorizatsiya talab qilinadi"


class InvalidDeviceSignatureError(AuthenticationError):
    code = "invalid_device_signature"
    message = "Qurilma imzosi noto'g'ri"


class TokenExpiredError(AuthenticationError):
    """Access token muddati o'tgan — mijoz refresh qiladi."""

    code = "token_expired"
    message = "Kirish tokeni muddati o'tdi"


class SessionExpiredError(AuthenticationError):
    """Refresh token muddati o'tgan yoki sessiya yo'q — UI "Session expired" holati."""

    code = "session_expired"
    message = "Sessiya tugadi. Qayta kiring"


class TokenReuseDetectedError(AuthenticationError):
    code = "session_revoked"
    message = "Sessiya bekor qilindi. Qayta kiring"


class ServiceUnavailableError(DomainError):
    """Tashqi xizmat (SMS provayderi va h.k.) ishlamayapti. Tafsilot mijozga aytilmaydi."""

    code = "service_unavailable"
    message = "Xizmat vaqtincha ishlamayapti. Keyinroq urinib ko'ring"


class AiUnavailableError(ServiceUnavailableError):
    code = "ai_unavailable"
    message = "Yordamchi hozir ishlamayapti"


class OcrUnavailableError(ServiceUnavailableError):
    code = "ocr_unavailable"
    message = "Chekni o'qish xizmati ishlamayapti"


class ReceiptUnreadableError(DomainError):
    code = "receipt_unreadable"
    message = "Chekni o'qib bo'lmadi"


class QrNotSupportedError(DomainError):
    code = "qr_not_supported"
    message = "Bu QR fiskal chek emas"


class AccountFrozenError(DomainError):
    code = "account_frozen"
    message = "Bu hisob muzlatilgan"


class ConflictError(DomainError):
    code = "conflict"
    message = "Bunday yozuv allaqachon mavjud"


class CategoryInUseError(ConflictError):
    code = "category_in_use"
    message = "Kategoriyada tranzaksiyalar bor. Ularni qayerga o'tkazishni tanlang"


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
