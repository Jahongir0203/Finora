"""IP geolokatsiya (BE-105). MaxMind/ipinfo bazasi ulanmaguncha shahar noma'lum (None).

IP'ning o'zi saqlanmaydi — faqat shahar nomi (qurilmalar ro'yxati va "New sign-in" uchun).
"""


class NoopGeoLocator:
    async def city(self, ip: str) -> str | None:
        return None
