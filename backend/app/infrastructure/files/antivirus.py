"""Antivirus skani (02-backend.md, 6-bo'lim). clamd INSTREAM protokoli orqali."""

import asyncio
import logging
import struct

from app.core.config import Environment, Settings

logger = logging.getLogger("finora.files")

_CHUNK = 64 * 1024


class ClamAvScanner:
    def __init__(self, host: str, port: int, timeout: float = 30.0) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout

    async def is_clean(self, data: bytes) -> bool:
        async with asyncio.timeout(self._timeout):
            reader, writer = await asyncio.open_connection(self._host, self._port)
            try:
                writer.write(b"zINSTREAM\0")
                for i in range(0, len(data), _CHUNK):
                    chunk = data[i:i + _CHUNK]
                    writer.write(struct.pack(">I", len(chunk)) + chunk)
                writer.write(struct.pack(">I", 0))
                await writer.drain()
                reply = (await reader.read(4096)).rstrip(b"\0").decode(errors="replace")
            finally:
                writer.close()
                await writer.wait_closed()
        if reply.endswith("OK"):
            return True
        if reply.endswith("FOUND"):
            logger.warning("receipt_malware_detected", extra={"event": "alert.malware"})
            return False
        # Skaner xatosi — fail-closed: fayl qabul qilinmaydi
        raise RuntimeError("clamd javobi tushunarsiz")


class NoopScanner:
    """Faqat dev/test: ClamAV o'rnatilmagan muhit uchun. Prod'da ishga tushmaydi."""

    def __init__(self, settings: Settings) -> None:
        if settings.env is Environment.PROD:
            raise RuntimeError("NoopScanner prod'da taqiqlangan")

    async def is_clean(self, data: bytes) -> bool:
        return True
