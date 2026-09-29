"""O'z botimiz orqali OTP.

Ulash (bir marta): /start -> "Raqamni ulashish" tugmasi (request_contact) -> bot foydalanuvchining
O'Z raqamini oladi (contact.user_id == from.id tekshiriladi, aks holda begona raqam kodini olish
mumkin bo'lardi) -> `telegram_links`ga blind index bilan yoziladi.

Yuborish: raqam ulangan bo'lsa kod botdan keladi; ulanmagan / bot bloklangan / Telegram
ishlamasa — SMS. Limitlar (60 s, 5 urinish, 15 daq blok) kanalga bog'liq emas.
"""

import logging
from collections.abc import Callable
from typing import Any

from app.application.common.audit import record_audit
from app.application.common.interfaces import (
    Clock,
    SecretHasher,
    TelegramBot,
    TelegramChatUnavailable,
)
from app.application.common.uow import UnitOfWork
from app.core.i18n import DEFAULT_LANGUAGE, normalize_language, t
from app.domain.audit.entities import AuditAction
from app.domain.common.errors import ServiceUnavailableError, ValidationFailedError
from app.domain.common.values import PhoneNumber
from app.domain.telegram.entities import TelegramLink

logger = logging.getLogger("finora.telegram")


class TelegramOtpChannel:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], bot: TelegramBot) -> None:
        self._uow = uow_factory
        self._bot = bot

    async def try_send(self, phone_index: str, code: str) -> bool:
        """True — kod Telegram'ga yetkazildi (SMS kerak emas)."""
        async with self._uow() as uow:
            link = await uow.telegram_links.get(phone_index)
        if link is None:
            return False
        try:
            await self._bot.send_message(link.chat_id, t("telegram.code", link.language,
                                                         code=code))
        except TelegramChatUnavailable:
            logger.info("telegram_chat_unavailable")
            async with self._uow() as uow:
                await uow.telegram_links.delete_by_chat(link.chat_id)
                await uow.commit()
            return False
        except ServiceUnavailableError:
            return False
        logger.info("otp_sent_telegram")
        return True


def _share_keyboard(locale: str) -> dict[str, Any]:
    return {"keyboard": [[{"text": t("telegram.share_button", locale), "request_contact": True}]],
            "resize_keyboard": True, "one_time_keyboard": True}


class TelegramWebhook:
    """Telegram update'larini qayta ishlaydi. Har doim jim tugaydi — Telegram xatoda qayta
    yuboradi, shuning uchun noma'lum update'lar e'tiborsiz qoldiriladi."""

    def __init__(self, uow_factory: Callable[[], UnitOfWork], bot: TelegramBot,
                 hasher: SecretHasher, clock: Clock) -> None:
        self._uow = uow_factory
        self._bot = bot
        self._hasher = hasher
        self._clock = clock

    async def handle(self, update: dict[str, Any]) -> None:
        member = update.get("my_chat_member")
        if isinstance(member, dict):
            await self._on_member(member)
            return
        message = update.get("message")
        if not isinstance(message, dict):
            return
        chat = message.get("chat") or {}
        sender = message.get("from") or {}
        # Faqat shaxsiy chat (guruhga qo'shilgan bot kod yubormaydi)
        if chat.get("type") != "private" or not isinstance(chat.get("id"), int):
            return
        locale = normalize_language(sender.get("language_code")) or DEFAULT_LANGUAGE
        chat_id: int = chat["id"]
        if isinstance(message.get("contact"), dict):
            await self._on_contact(chat_id, sender, message["contact"], locale)
            return
        text = message.get("text")
        if isinstance(text, str) and text.startswith("/stop"):
            await self._unlink(chat_id)
            await self._reply(chat_id, t("telegram.unlinked", locale))
            return
        # /start (deep link bilan ham) va boshqa har qanday matn — ulash taklifi
        await self._reply(chat_id, t("telegram.welcome", locale), _share_keyboard(locale))

    async def _on_contact(self, chat_id: int, sender: dict[str, Any],
                          contact: dict[str, Any], locale: str) -> None:
        # Faqat o'z raqami: "Kontaktni yuborish" orqali begona raqam ham yuborish mumkin
        if contact.get("user_id") is None or contact.get("user_id") != sender.get("id"):
            logger.warning("telegram_foreign_contact")
            await self._reply(chat_id, t("telegram.not_own", locale), _share_keyboard(locale))
            return
        try:
            phone = PhoneNumber.parse(str(contact.get("phone_number", "")))
        except ValidationFailedError:
            await self._reply(chat_id, t("telegram.not_uz", locale))
            return
        idx = self._hasher.phone_index(phone)
        async with self._uow() as uow:
            await uow.telegram_links.save(TelegramLink(
                phone_index=idx, chat_id=chat_id, telegram_user_id=int(sender["id"]),
                language=locale, linked_at=self._clock.now()))
            user = await uow.users.get_by_phone_index(idx)
            await record_audit(uow, self._clock, AuditAction.TELEGRAM_LINKED,
                               user_id=user.id if user else None)
            await uow.commit()
        logger.info("telegram_linked")
        await self._reply(chat_id, t("telegram.linked", locale), {"remove_keyboard": True})

    async def _on_member(self, member: dict[str, Any]) -> None:
        """Foydalanuvchi botni bloklasa (kicked) — bog'lanish o'chiriladi."""
        status = (member.get("new_chat_member") or {}).get("status")
        chat_id = (member.get("chat") or {}).get("id")
        if status == "kicked" and isinstance(chat_id, int):
            await self._unlink(chat_id)

    async def _unlink(self, chat_id: int) -> None:
        async with self._uow() as uow:
            await uow.telegram_links.delete_by_chat(chat_id)
            await uow.commit()

    async def _reply(self, chat_id: int, text: str,
                     markup: dict[str, Any] | None = None) -> None:
        try:
            await self._bot.send_message(chat_id, text, markup)
        except (TelegramChatUnavailable, ServiceUnavailableError):
            logger.info("telegram_reply_failed")
