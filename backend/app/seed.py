"""Seed ma'lumotlari (BE-001): FAQ (BE-1701).

    uv run python -m app.seed

Tizim kategoriyalari, valyutalar va tillar kodda (app/domain/...) — seed talab qilmaydi.
Idempotent: har tilning FAQ ro'yxati to'liq almashtiriladi.
"""

import asyncio
import uuid

from app.container import build_container
from app.core.config import get_settings
from app.domain.help.entities import FaqItem

# Dizayndagi 5 ta savol (PROFILE_SETTINGS.md, 8-bo'lim). "Karta qo'shish" javobi xavfsizlik
# talabiga moslangan: to'liq karta raqami so'ralmaydi (02-backend.md, BE-1401).
FAQ: dict[str, list[tuple[str, str]]] = {
    "en": [
        ("How do I add a card?",
         "Open Profile → Accounts & cards and tap +. Choose the bank and network, enter the last "
         "4 digits and the expiry date. Finora never asks for the full card number."),
        ("Is my data safe?",
         "Your data is encrypted on the device and on our servers. The app is protected by your "
         "PIN or Face ID, and Finora never shares your transactions with anyone."),
        ("How do payment reminders work?",
         "Add a bill in Payment reminders with its amount, due date and how often it repeats. "
         "We notify you a day before and on the due day."),
        ("How do I export my transactions?",
         "Tap the download button on Activity or Statistics, or open Profile → Export data. "
         "Pick a period and a format: PDF, Excel or CSV."),
        ("Can I change my primary currency?",
         "Yes. Open Profile → Primary currency and pick a new one. Amounts are stored in UZS and "
         "shown in your currency at the daily Central Bank rate."),
    ],
    "uz-Latn": [
        ("Kartani qanday qo'shaman?",
         "Profil → Hisoblar va kartalar bo'limida + tugmasini bosing. Bank va turini tanlang, "
         "oxirgi 4 raqam va amal qilish muddatini kiriting. Finora to'liq karta raqamini "
         "hech qachon so'ramaydi."),
        ("Ma'lumotlarim xavfsizmi?",
         "Ma'lumotlaringiz qurilmada va serverlarimizda shifrlangan. Ilova PIN yoki Face ID "
         "bilan himoyalangan, Finora tranzaksiyalaringizni hech kimga bermaydi."),
        ("To'lov eslatmalari qanday ishlaydi?",
         "To'lov eslatmalari bo'limida summa, sana va takrorlanishni kiriting. Sanadan bir kun "
         "oldin va shu kuni xabar yuboramiz."),
        ("Tranzaksiyalarni qanday eksport qilaman?",
         "Activity yoki Statistika sahifasidagi yuklab olish tugmasini bosing yoki Profil → "
         "Eksport bo'limini oching. Davr va formatni tanlang: PDF, Excel yoki CSV."),
        ("Asosiy valyutani o'zgartirsa bo'ladimi?",
         "Ha. Profil → Asosiy valyuta bo'limida yangisini tanlang. Summalar so'mda saqlanadi va "
         "Markaziy bankning kunlik kursi bo'yicha ko'rsatiladi."),
    ],
    "ru": [
        ("Как добавить карту?",
         "Откройте Профиль → Счета и карты и нажмите +. Выберите банк и платёжную систему, "
         "введите последние 4 цифры и срок действия. Finora никогда не запрашивает полный "
         "номер карты."),
        ("Мои данные в безопасности?",
         "Данные зашифрованы на устройстве и на наших серверах. Приложение защищено PIN-кодом "
         "или Face ID, Finora никому не передаёт ваши операции."),
        ("Как работают напоминания о платежах?",
         "Добавьте платёж в Напоминаниях: сумму, дату и периодичность. Мы напомним за день и "
         "в день платежа."),
        ("Как экспортировать операции?",
         "Нажмите кнопку загрузки в Активности или Статистике либо откройте Профиль → Экспорт. "
         "Выберите период и формат: PDF, Excel или CSV."),
        ("Можно ли сменить основную валюту?",
         "Да. Откройте Профиль → Основная валюта и выберите новую. Суммы хранятся в сумах и "
         "показываются по дневному курсу ЦБ."),
    ],
}


async def seed_faq() -> int:
    container = build_container(get_settings())
    try:
        total = 0
        async with container.uow() as uow:
            for lang, items in FAQ.items():
                await uow.faq.replace_language(lang, [
                    FaqItem(id=uuid.uuid4(), language=lang, question=q, answer=a, position=i)
                    for i, (q, a) in enumerate(items)])
                total += len(items)
            await uow.commit()
        return total
    finally:
        await container.aclose()


if __name__ == "__main__":
    print(f"FAQ: {asyncio.run(seed_faq())} ta yozuv")
