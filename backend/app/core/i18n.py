"""Server matnlari lokalizatsiyasi (BE-1601).

Qo'llab-quvvatlanadigan tillar: en, uz-Latn, uz-Cyrl, ru, kk, tr.
- So'rov tili `Accept-Language`dan (xato xabarlari), fon vazifalari uchun `user.language`dan.
- uz-Cyrl alohida yozilmaydi: uz-Latn matni qoidaga ko'ra kirillga o'giriladi.
- Kalit topilmasa — inglizcha matn, u ham bo'lmasa kalitning o'zi.
"""

import re
from contextvars import ContextVar
from typing import Any

SUPPORTED_LANGUAGES = ("en", "uz-Latn", "uz-Cyrl", "ru", "kk", "tr")
DEFAULT_LANGUAGE = "uz-Latn"

locale_ctx: ContextVar[str] = ContextVar("locale", default=DEFAULT_LANGUAGE)
# So'rovda Accept-Language aniq berilganmi (aks holda user.language ishlatiladi)
locale_explicit_ctx: ContextVar[bool] = ContextVar("locale_explicit", default=False)

_ALIASES = {
    "en": "en", "uz": "uz-Latn", "uz-latn": "uz-Latn", "uz-cyrl": "uz-Cyrl", "ru": "ru",
    "kk": "kk", "kz": "kk", "tr": "tr",
}


def normalize_language(tag: str | None) -> str | None:
    """"uz-UZ", "ru_RU", "uz-Cyrl-UZ" -> qo'llab-quvvatlanadigan kod yoki None."""
    if not tag:
        return None
    tag = tag.strip().replace("_", "-").lower()
    if tag.startswith("uz-cyrl"):
        return "uz-Cyrl"
    if tag in _ALIASES:
        return _ALIASES[tag]
    return _ALIASES.get(tag.split("-", 1)[0])


def parse_accept_language(header: str | None) -> str | None:
    if not header:
        return None
    weighted: list[tuple[float, str]] = []
    for part in header.split(",")[:10]:
        lang, _, q = part.strip().partition(";q=")
        try:
            weight = float(q) if q else 1.0
        except ValueError:
            continue
        if (code := normalize_language(lang)) is not None:
            weighted.append((weight, code))
    return max(weighted, key=lambda w: w[0])[1] if weighted else None


# --- uz-Latn -> uz-Cyrl -------------------------------------------------------------------
_APOS = "'ʻʼ‘’`"
_DIGRAPHS = [
    # Ruscha o'zlashmalar: -tsiya -> -ция, -tsion -> -цион (avtorizatsiya, operatsion)
    ("tsiya", "ция"), ("tsion", "цион"), ("ksiya", "кция"),
    (f"o[{_APOS}]", "ў"), (f"g[{_APOS}]", "ғ"), ("sh", "ш"), ("ch", "ч"), ("yo", "ё"),
    ("yu", "ю"), ("ya", "я"), ("ye", "е"),
]
_SINGLE = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и", "j": "ж",
    "k": "к", "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ", "r": "р", "s": "с",
    "t": "т", "u": "у", "v": "в", "x": "х", "y": "й", "z": "з",
}
_TOKEN = re.compile(r"\{[^}]*\}|[A-Za-z" + _APOS + r"]+")


def _match_case(src: str, dst: str) -> str:
    if src.isupper() and len(src) > 1:
        return dst.upper()
    return dst[0].upper() + dst[1:] if src[:1].isupper() else dst


def _translit_word(word: str) -> str:
    out: list[str] = []
    i, lower = 0, word.lower()
    while i < len(word):
        for pattern, cyr in _DIGRAPHS:
            m = re.match(pattern, lower[i:])
            if m:
                out.append(_match_case(word[i:i + m.end()], cyr))
                i += m.end()
                break
        else:
            ch = lower[i]
            if ch == "e" and i == 0:
                cyr = "э"  # so'z boshidagi e -> э
            elif ch in _APOS:
                cyr = "ъ"
            else:
                cyr = _SINGLE.get(ch, word[i])
            out.append(_match_case(word[i], cyr) if cyr != word[i] else cyr)
            i += 1
    return "".join(out)


def latin_to_cyrillic(text: str) -> str:
    """Placeholder'lar ({name}) o'zgarmaydi."""
    return _TOKEN.sub(
        lambda m: m.group(0) if m.group(0).startswith("{") else _translit_word(m.group(0)), text
    )


# --- Katalog ------------------------------------------------------------------------------
# Har kalit: {til: matn}. uz-Cyrl avtomatik. Parametrlar str.format_map orqali.
_C: dict[str, dict[str, str]] = {
    # Xatolar (BE-1801)
    "error.not_found": {
        "en": "Not found", "uz-Latn": "Resurs topilmadi", "ru": "Не найдено",
        "kk": "Табылмады", "tr": "Bulunamadı"},
    "error.validation_error": {
        "en": "Some fields are invalid", "uz-Latn": "Ma'lumot noto'g'ri",
        "ru": "Некорректные данные", "kk": "Деректер қате", "tr": "Bazı alanlar geçersiz"},
    "error.insufficient_funds": {
        "en": "Amount exceeds the saved balance",
        "uz-Latn": "Yechish summasi jamg'armadan oshib ketdi",
        "ru": "Сумма превышает накопленное", "kk": "Сома жинақтан асып кетті",
        "tr": "Tutar birikimi aşıyor"},
    "error.rate_limited": {
        "en": "Too many requests. Try again later",
        "uz-Latn": "Juda ko'p so'rov. Keyinroq urinib ko'ring",
        "ru": "Слишком много запросов. Попробуйте позже",
        "kk": "Сұраулар тым көп. Кейінірек көріңіз",
        "tr": "Çok fazla istek. Daha sonra tekrar deneyin"},
    "error.otp_blocked": {
        "en": "Too many wrong attempts. The number is temporarily blocked",
        "uz-Latn": "Juda ko'p noto'g'ri urinish. Raqam vaqtincha bloklandi",
        "ru": "Слишком много неверных попыток. Номер временно заблокирован",
        "kk": "Қате әрекет тым көп. Нөмір уақытша бұғатталды",
        "tr": "Çok fazla hatalı deneme. Numara geçici olarak engellendi"},
    "error.otp_invalid": {
        "en": "Wrong code", "uz-Latn": "Kod noto'g'ri", "ru": "Неверный код",
        "kk": "Код қате", "tr": "Kod hatalı"},
    "error.otp_expired": {
        "en": "The code has expired. Request a new one",
        "uz-Latn": "Kod muddati o'tdi. Yangisini so'rang",
        "ru": "Срок действия кода истёк. Запросите новый",
        "kk": "Кодтың мерзімі өтті. Жаңасын сұраңыз",
        "tr": "Kodun süresi doldu. Yeni kod isteyin"},
    "error.unauthorized": {
        "en": "Authorization required", "uz-Latn": "Avtorizatsiya talab qilinadi",
        "ru": "Требуется авторизация", "kk": "Авторизация қажет", "tr": "Yetkilendirme gerekli"},
    "error.token_expired": {
        "en": "Access token expired", "uz-Latn": "Kirish tokeni muddati o'tdi",
        "ru": "Срок действия токена истёк", "kk": "Токен мерзімі өтті",
        "tr": "Erişim belirtecinin süresi doldu"},
    "error.session_expired": {
        "en": "Session expired. Sign in again", "uz-Latn": "Sessiya tugadi. Qayta kiring",
        "ru": "Сессия истекла. Войдите снова", "kk": "Сессия аяқталды. Қайта кіріңіз",
        "tr": "Oturum sona erdi. Tekrar giriş yapın"},
    "error.session_revoked": {
        "en": "Session was revoked. Sign in again",
        "uz-Latn": "Sessiya bekor qilindi. Qayta kiring",
        "ru": "Сессия отозвана. Войдите снова", "kk": "Сессия жойылды. Қайта кіріңіз",
        "tr": "Oturum iptal edildi. Tekrar giriş yapın"},
    "error.invalid_device_signature": {
        "en": "Invalid device signature", "uz-Latn": "Qurilma imzosi noto'g'ri",
        "ru": "Неверная подпись устройства", "kk": "Құрылғы қолтаңбасы қате",
        "tr": "Geçersiz cihaz imzası"},
    "error.service_unavailable": {
        "en": "Service is temporarily unavailable",
        "uz-Latn": "Xizmat vaqtincha ishlamayapti. Keyinroq urinib ko'ring",
        "ru": "Сервис временно недоступен", "kk": "Қызмет уақытша қолжетімсіз",
        "tr": "Hizmet geçici olarak kullanılamıyor"},
    "error.ai_unavailable": {
        "en": "The assistant is unavailable right now",
        "uz-Latn": "Yordamchi hozir ishlamayapti", "ru": "Ассистент сейчас недоступен",
        "kk": "Көмекші қазір қолжетімсіз", "tr": "Asistan şu anda kullanılamıyor"},
    "error.ocr_unavailable": {
        "en": "Receipt recognition is unavailable", "uz-Latn": "Chekni o'qish xizmati ishlamayapti",
        "ru": "Распознавание чеков недоступно", "kk": "Чекті тану қолжетімсіз",
        "tr": "Fiş tanıma kullanılamıyor"},
    "error.conflict": {
        "en": "Already exists", "uz-Latn": "Bunday yozuv allaqachon mavjud",
        "ru": "Уже существует", "kk": "Бұрыннан бар", "tr": "Zaten mevcut"},
    "error.unsupported_media_type": {
        "en": "Only JPEG, PNG or HEIC images are accepted",
        "uz-Latn": "Faqat JPEG, PNG yoki HEIC rasm qabul qilinadi",
        "ru": "Принимаются только JPEG, PNG или HEIC", "kk": "Тек JPEG, PNG немесе HEIC",
        "tr": "Yalnızca JPEG, PNG veya HEIC kabul edilir"},
    "error.file_rejected": {
        "en": "File was rejected", "uz-Latn": "Fayl qabul qilinmadi", "ru": "Файл отклонён",
        "kk": "Файл қабылданбады", "tr": "Dosya reddedildi"},
    "error.receipt_unreadable": {
        "en": "Couldn't read the receipt", "uz-Latn": "Chekni o'qib bo'lmadi",
        "ru": "Не удалось прочитать чек", "kk": "Чекті оқу мүмкін болмады",
        "tr": "Fiş okunamadı"},
    "error.qr_not_supported": {
        "en": "This QR code is not a fiscal receipt", "uz-Latn": "Bu QR fiskal chek emas",
        "ru": "Этот QR-код не фискальный чек", "kk": "Бұл QR фискалдық чек емес",
        "tr": "Bu QR kod mali fiş değil"},
    "error.idempotency_key_required": {
        "en": "Idempotency-Key header is required",
        "uz-Latn": "Idempotency-Key sarlavhasi majburiy",
        "ru": "Требуется заголовок Idempotency-Key", "kk": "Idempotency-Key тақырыбы қажет",
        "tr": "Idempotency-Key başlığı gerekli"},
    "error.idempotency_conflict": {
        "en": "This Idempotency-Key was used with another request",
        "uz-Latn": "Bu Idempotency-Key boshqa so'rov bilan ishlatilgan",
        "ru": "Этот Idempotency-Key уже использован с другим запросом",
        "kk": "Бұл Idempotency-Key басқа сұрауда қолданылған",
        "tr": "Bu Idempotency-Key başka bir istekte kullanıldı"},
    "error.account_frozen": {
        "en": "This account is frozen", "uz-Latn": "Bu hisob muzlatilgan",
        "ru": "Этот счёт заморожен", "kk": "Бұл шот бұғатталған", "tr": "Bu hesap donduruldu"},
    "error.category_type_mismatch": {
        "en": "Category does not match the transaction type",
        "uz-Latn": "Kategoriya tranzaksiya turiga mos emas",
        "ru": "Категория не соответствует типу операции",
        "kk": "Санат операция түріне сәйкес емес",
        "tr": "Kategori işlem türüyle uyuşmuyor"},
    "error.goal_name_required": {
        "en": "Give the goal a name", "uz-Latn": "Maqsadga nom bering",
        "ru": "Укажите название цели", "kk": "Мақсатқа атау беріңіз",
        "tr": "Hedefe bir ad verin"},
    "error.goal_target_min": {
        "en": "Target must be at least 100 000 UZS",
        "uz-Latn": "Maqsad summasi kamida 100 000 so'm",
        "ru": "Цель — не менее 100 000 сум", "kk": "Мақсат кемінде 100 000 сум",
        "tr": "Hedef en az 100 000 UZS olmalı"},
    "error.category_name_required": {
        "en": "Give the category a name", "uz-Latn": "Kategoriyaga nom bering",
        "ru": "Укажите название категории", "kk": "Санатқа атау беріңіз",
        "tr": "Kategoriye bir ad verin"},
    "error.category_in_use": {
        "en": "Category has transactions. Choose where to move them",
        "uz-Latn": "Kategoriyada tranzaksiyalar bor. Ularni qayerga o'tkazishni tanlang",
        "ru": "В категории есть операции. Выберите, куда их перенести",
        "kk": "Санатта операциялар бар. Оларды қайда ауыстыру керектігін таңдаңыз",
        "tr": "Kategoride işlemler var. Nereye taşınacağını seçin"},
    "error.payload_too_large": {
        "en": "Request is too large", "uz-Latn": "So'rov hajmi juda katta",
        "ru": "Слишком большой запрос", "kk": "Сұрау тым үлкен", "tr": "İstek çok büyük"},
    "error.internal_error": {
        "en": "Something went wrong. Try again later",
        "uz-Latn": "Ichki xatolik. Keyinroq urinib ko'ring",
        "ru": "Внутренняя ошибка. Попробуйте позже", "kk": "Ішкі қате. Кейінірек көріңіз",
        "tr": "Bir şeyler ters gitti. Daha sonra deneyin"},

    # Kategoriyalar (BE-1501)
    "category.groceries": {"en": "Groceries", "uz-Latn": "Oziq-ovqat", "ru": "Продукты",
                           "kk": "Азық-түлік", "tr": "Market"},
    "category.food": {"en": "Food & drinks", "uz-Latn": "Kafe va restoran",
                      "ru": "Кафе и рестораны", "kk": "Тамақ және сусын",
                      "tr": "Yeme & içme"},
    "category.transport": {"en": "Transport", "uz-Latn": "Transport", "ru": "Транспорт",
                           "kk": "Көлік", "tr": "Ulaşım"},
    "category.bills": {"en": "Bills", "uz-Latn": "Kommunal to'lovlar",
                       "ru": "Счета и коммунальные", "kk": "Төлемдер", "tr": "Faturalar"},
    "category.health": {"en": "Health", "uz-Latn": "Salomatlik", "ru": "Здоровье",
                        "kk": "Денсаулық", "tr": "Sağlık"},
    "category.shopping": {"en": "Shopping", "uz-Latn": "Xaridlar", "ru": "Покупки",
                          "kk": "Сауда", "tr": "Alışveriş"},
    "category.housing": {"en": "Housing", "uz-Latn": "Uy-joy", "ru": "Жильё",
                         "kk": "Тұрғын үй", "tr": "Konut"},
    "category.subs": {"en": "Subscriptions", "uz-Latn": "Obunalar", "ru": "Подписки",
                      "kk": "Жазылымдар", "tr": "Abonelikler"},
    "category.salary": {"en": "Salary", "uz-Latn": "Maosh", "ru": "Зарплата",
                        "kk": "Жалақы", "tr": "Maaş"},
    "category.transfer": {"en": "Transfers", "uz-Latn": "O'tkazmalar", "ru": "Переводы",
                          "kk": "Аударымдар", "tr": "Transferler"},

    # Hisoblar
    "account.cash": {"en": "Cash", "uz-Latn": "Naqd pul", "ru": "Наличные",
                     "kk": "Қолма-қол", "tr": "Nakit"},
    "account.card": {"en": "Card", "uz-Latn": "Karta", "ru": "Карта", "kk": "Карта",
                     "tr": "Kart"},

    # Bildirishnomalar (BE-403)
    "notif.payment_due.title": {
        "en": "{title} is due {when}", "uz-Latn": "{title} to'lovi {when}",
        "ru": "Платёж «{title}» {when}", "kk": "«{title}» төлемі {when}",
        "tr": "{title} ödemesi {when}"},
    "notif.payment_due.body": {
        "en": "{amount} UZS · {date}", "uz-Latn": "{amount} so'm · {date}",
        "ru": "{amount} сум · {date}", "kk": "{amount} сум · {date}",
        "tr": "{amount} UZS · {date}"},
    "notif.when.today": {"en": "today", "uz-Latn": "bugun", "ru": "сегодня",
                         "kk": "бүгін", "tr": "bugün"},
    "notif.when.tomorrow": {"en": "tomorrow", "uz-Latn": "ertaga", "ru": "завтра",
                            "kk": "ертең", "tr": "yarın"},
    "notif.income.title": {"en": "Income received", "uz-Latn": "Kirim tushdi",
                           "ru": "Поступление средств", "kk": "Кіріс түсті",
                           "tr": "Gelir alındı"},
    "notif.income.body": {
        "en": "{amount} UZS from {source} arrived on {card}",
        "uz-Latn": "{source}dan {amount} so'm {card} kartaga tushdi",
        "ru": "{amount} сум от {source} зачислено на {card}",
        "kk": "{source} жіберген {amount} сум {card} картасына түсті",
        "tr": "{source} kaynağından {amount} UZS {card} kartına geldi"},
    "notif.budget_warning.title": {
        "en": "{category}: 75% of budget used", "uz-Latn": "{category}: byudjetning 75% sarflandi",
        "ru": "{category}: израсходовано 75% бюджета", "kk": "{category}: бюджеттің 75% жұмсалды",
        "tr": "{category}: bütçenin %75'i kullanıldı"},
    "notif.budget_exceeded.title": {
        "en": "{category} budget exceeded", "uz-Latn": "{category} byudjeti oshib ketdi",
        "ru": "Бюджет «{category}» превышен", "kk": "«{category}» бюджеті асып кетті",
        "tr": "{category} bütçesi aşıldı"},
    "notif.budget.body": {
        "en": "Spent {spent} of {limit} UZS this month",
        "uz-Latn": "Bu oy {limit} so'mdan {spent} so'm sarflandi",
        "ru": "В этом месяце потрачено {spent} из {limit} сум",
        "kk": "Осы айда {limit} сумның {spent} сумы жұмсалды",
        "tr": "Bu ay {limit} UZS'nin {spent} UZS'si harcandı"},
    "notif.weekly_report.title": {
        "en": "Your weekly report", "uz-Latn": "Haftalik hisobot", "ru": "Недельный отчёт",
        "kk": "Апталық есеп", "tr": "Haftalık raporunuz"},
    "notif.weekly_report.up": {
        "en": "You spent {pct}% more than the week before",
        "uz-Latn": "O'tgan haftadan {pct}% ko'p sarfladingiz",
        "ru": "Вы потратили на {pct}% больше, чем неделей ранее",
        "kk": "Алдыңғы аптадан {pct}% көп жұмсадыңыз",
        "tr": "Önceki haftadan %{pct} daha fazla harcadınız"},
    "notif.weekly_report.down": {
        "en": "You spent {pct}% less than the week before",
        "uz-Latn": "O'tgan haftadan {pct}% kam sarfladingiz",
        "ru": "Вы потратили на {pct}% меньше, чем неделей ранее",
        "kk": "Алдыңғы аптадан {pct}% аз жұмсадыңыз",
        "tr": "Önceki haftadan %{pct} daha az harcadınız"},
    "notif.weekly_report.same": {
        "en": "You spent {amount} UZS last week",
        "uz-Latn": "O'tgan hafta {amount} so'm sarfladingiz",
        "ru": "За прошлую неделю потрачено {amount} сум",
        "kk": "Өткен аптада {amount} сум жұмсадыңыз",
        "tr": "Geçen hafta {amount} UZS harcadınız"},
    "notif.goal_milestone.title": {
        "en": "{goal}: {pct}% reached", "uz-Latn": "{goal}: {pct}% ga yetdingiz",
        "ru": "{goal}: достигнуто {pct}%", "kk": "{goal}: {pct}% орындалды",
        "tr": "{goal}: %{pct} tamamlandı"},
    "notif.goal_milestone.body": {
        "en": "Keep going — you're getting closer", "uz-Latn": "Davom eting — maqsad yaqin",
        "ru": "Продолжайте — цель всё ближе", "kk": "Жалғастырыңыз — мақсат жақын",
        "tr": "Devam edin — hedefe yaklaşıyorsunuz"},
    "notif.goal_completed.body": {
        "en": "Goal completed. Congratulations!", "uz-Latn": "Maqsad bajarildi. Tabriklaymiz!",
        "ru": "Цель достигнута. Поздравляем!", "kk": "Мақсат орындалды. Құттықтаймыз!",
        "tr": "Hedef tamamlandı. Tebrikler!"},
    "notif.autosave_skipped.title": {
        "en": "Auto-save skipped", "uz-Latn": "Avto-jamg'arma o'tkazib yuborildi",
        "ru": "Автосбережение пропущено", "kk": "Автожинақ өткізілді",
        "tr": "Otomatik birikim atlandı"},
    "notif.autosave_skipped.body": {
        "en": "Not enough money on the account for {goal}",
        "uz-Latn": "{goal} uchun hisobda mablag' yetmadi",
        "ru": "Недостаточно средств на счёте для цели «{goal}»",
        "kk": "«{goal}» үшін шотта қаражат жетпеді",
        "tr": "{goal} için hesapta yeterli para yok"},
    "notif.security.new_sign_in.title": {
        "en": "New sign-in", "uz-Latn": "Yangi kirish", "ru": "Новый вход",
        "kk": "Жаңа кіру", "tr": "Yeni oturum açma"},
    "notif.security.new_sign_in.body": {
        "en": "Finora was opened on a new device{where}: {device}",
        "uz-Latn": "Finora yangi qurilmada ochildi{where}: {device}",
        "ru": "Finora открыта на новом устройстве{where}: {device}",
        "kk": "Finora жаңа құрылғыда ашылды{where}: {device}",
        "tr": "Finora yeni bir cihazda açıldı{where}: {device}"},
    "notif.security.where": {"en": " in {city}", "uz-Latn": " ({city})", "ru": " ({city})",
                             "kk": " ({city})", "tr": " ({city})"},
    "notif.security.push_body": {
        "en": "Your account was opened on a new device. Open the app.",
        "uz-Latn": "Hisobingizga yangi qurilmadan kirildi. Ilovani oching.",
        "ru": "В ваш аккаунт вошли с нового устройства. Откройте приложение.",
        "kk": "Аккаунтыңызға жаңа құрылғыдан кірді. Қолданбаны ашыңыз.",
        "tr": "Hesabınıza yeni bir cihazdan girildi. Uygulamayı açın."},
    "notif.security.title": {
        "en": "Security alert", "uz-Latn": "Xavfsizlik ogohlantirishi",
        "ru": "Уведомление безопасности", "kk": "Қауіпсіздік ескертуі",
        "tr": "Güvenlik uyarısı"},
    "notif.security.refresh_reuse": {
        "en": "All sessions were closed for your safety. Sign in again.",
        "uz-Latn": "Xavfsizlik uchun barcha sessiyalar yopildi. Qayta kiring.",
        "ru": "В целях безопасности все сессии закрыты. Войдите снова.",
        "kk": "Қауіпсіздік үшін барлық сессиялар жабылды. Қайта кіріңіз.",
        "tr": "Güvenliğiniz için tüm oturumlar kapatıldı. Tekrar giriş yapın."},
    "notif.security.pin_failures": {
        "en": "Too many wrong PIN attempts. The device session was closed.",
        "uz-Latn": "Ko'p marta noto'g'ri PIN kiritildi. Qurilma sessiyasi yopildi.",
        "ru": "Слишком много неверных PIN. Сессия устройства закрыта.",
        "kk": "PIN тым көп рет қате енгізілді. Құрылғы сессиясы жабылды.",
        "tr": "Çok fazla hatalı PIN. Cihaz oturumu kapatıldı."},
    "notif.security.pin_reset": {
        "en": "PIN was reset on {device}", "uz-Latn": "{device} qurilmasida PIN tiklandi",
        "ru": "PIN сброшен на устройстве {device}",
        "kk": "{device} құрылғысында PIN қалпына келтірілді",
        "tr": "{device} cihazında PIN sıfırlandı"},
    "notif.security.logout_all": {
        "en": "You signed out of all other devices",
        "uz-Latn": "Boshqa barcha qurilmalardan chiqdingiz",
        "ru": "Вы вышли на всех остальных устройствах",
        "kk": "Басқа барлық құрылғылардан шықтыңыз",
        "tr": "Diğer tüm cihazlardan çıkış yaptınız"},

    # Eksport (BE-602)
    "export.title": {"en": "Finora report", "uz-Latn": "Finora hisoboti", "ru": "Отчёт Finora",
                     "kk": "Finora есебі", "tr": "Finora raporu"},
    "export.period": {"en": "Period", "uz-Latn": "Davr", "ru": "Период", "kk": "Кезең",
                      "tr": "Dönem"},
    "export.income": {"en": "Income", "uz-Latn": "Kirim", "ru": "Доходы", "kk": "Кіріс",
                      "tr": "Gelir"},
    "export.expenses": {"en": "Expenses", "uz-Latn": "Chiqim", "ru": "Расходы",
                        "kk": "Шығыс", "tr": "Gider"},
    "export.net": {"en": "Net", "uz-Latn": "Sof", "ru": "Итого", "kk": "Таза", "tr": "Net"},
    "export.by_category": {"en": "By category", "uz-Latn": "Kategoriyalar bo'yicha",
                           "ru": "По категориям", "kk": "Санаттар бойынша",
                           "tr": "Kategoriye göre"},
    "export.transactions": {"en": "Transactions", "uz-Latn": "Tranzaksiyalar",
                            "ru": "Операции", "kk": "Операциялар", "tr": "İşlemler"},
    "export.summary": {"en": "Summary", "uz-Latn": "Xulosa", "ru": "Сводка",
                       "kk": "Қорытынды", "tr": "Özet"},
    "export.col.date": {"en": "Date", "uz-Latn": "Sana", "ru": "Дата", "kk": "Күні",
                        "tr": "Tarih"},
    "export.col.type": {"en": "Type", "uz-Latn": "Turi", "ru": "Тип", "kk": "Түрі",
                        "tr": "Tür"},
    "export.col.category": {"en": "Category", "uz-Latn": "Kategoriya", "ru": "Категория",
                            "kk": "Санат", "tr": "Kategori"},
    "export.col.title": {"en": "Title", "uz-Latn": "Nomi", "ru": "Название", "kk": "Атауы",
                         "tr": "Başlık"},
    "export.col.amount": {"en": "Amount (UZS)", "uz-Latn": "Summa (so'm)",
                          "ru": "Сумма (сум)", "kk": "Сома (сум)", "tr": "Tutar (UZS)"},
    "export.col.note": {"en": "Note", "uz-Latn": "Izoh", "ru": "Заметка", "kk": "Ескертпе",
                        "tr": "Not"},
    "export.col.share": {"en": "Share", "uz-Latn": "Ulush", "ru": "Доля", "kk": "Үлесі",
                         "tr": "Pay"},
    "type.expense": {"en": "Expense", "uz-Latn": "Chiqim", "ru": "Расход", "kk": "Шығыс",
                     "tr": "Gider"},
    "type.income": {"en": "Income", "uz-Latn": "Kirim", "ru": "Доход", "kk": "Кіріс",
                    "tr": "Gelir"},
    "type.transfer": {"en": "Transfer", "uz-Latn": "O'tkazma", "ru": "Перевод",
                      "kk": "Аударым", "tr": "Transfer"},

    # AI tavsiyalar (BE-901)
    "insight.overspend.title": {
        "en": "{category} is up {pct}%", "uz-Latn": "{category} xarajati {pct}% oshdi",
        "ru": "Расходы на «{category}» выросли на {pct}%",
        "kk": "«{category}» шығысы {pct}% өсті", "tr": "{category} harcaması %{pct} arttı"},
    "insight.overspend.body": {
        "en": "You spent {spent} UZS this month vs {avg} UZS on average. A budget can help.",
        "uz-Latn": "Bu oy {spent} so'm, o'rtacha {avg} so'm. Byudjet belgilash yordam beradi.",
        "ru": "В этом месяце {spent} сум при среднем {avg} сум. Поможет бюджет.",
        "kk": "Осы айда {spent} сум, орташа {avg} сум. Бюджет көмектеседі.",
        "tr": "Bu ay {spent} UZS, ortalama {avg} UZS. Bir bütçe yardımcı olabilir."},
    "insight.discount_days.title": {
        "en": "Shop groceries on discount days", "uz-Latn": "Oziq-ovqatni chegirma kunlari oling",
        "ru": "Покупайте продукты в дни скидок", "kk": "Азық-түлікті жеңілдік күндері алыңыз",
        "tr": "Market alışverişini indirim günlerinde yapın"},
    "insight.discount_days.body": {
        "en": "You made {count} grocery trips this month. Fewer, planned trips on discount "
              "days could save about {saving} UZS.",
        "uz-Latn": "Bu oy {count} marta oziq-ovqat oldingiz. Chegirma kunlariga "
                   "rejalashtirilgan xaridlar taxminan {saving} so'm tejaydi.",
        "ru": "В этом месяце {count} покупок продуктов. Плановые покупки в дни скидок "
              "сэкономят около {saving} сум.",
        "kk": "Осы айда {count} рет азық-түлік алдыңыз. Жеңілдік күндеріне жоспарлау "
              "шамамен {saving} сум үнемдейді.",
        "tr": "Bu ay {count} kez market alışverişi yaptınız. İndirim günlerinde planlı "
              "alışveriş yaklaşık {saving} UZS tasarruf sağlar."},
    "insight.subscriptions.title": {
        "en": "{count} subscriptions", "uz-Latn": "{count} ta obuna", "ru": "{count} подписки",
        "kk": "{count} жазылым", "tr": "{count} abonelik"},
    "insight.subscriptions.body": {
        "en": "You pay for {names}. Cancelling one could save {saving} UZS a month.",
        "uz-Latn": "{names} uchun to'layapsiz. Bittasidan voz kechish oyiga {saving} so'm tejaydi.",
        "ru": "Вы платите за {names}. Отказ от одной сэкономит {saving} сум в месяц.",
        "kk": "{names} үшін төлейсіз. Біреуінен бас тарту айына {saving} сум үнемдейді.",
        "tr": "{names} için ödüyorsunuz. Birini iptal etmek ayda {saving} UZS kazandırır."},
    "insight.autosave.title": {
        "en": "Turn on auto-save", "uz-Latn": "Avto-jamg'armani yoqing",
        "ru": "Включите автосбережение", "kk": "Автожинақты қосыңыз",
        "tr": "Otomatik birikimi açın"},
    "insight.autosave.body": {
        "en": "Saving {saving} UZS a month (10% of income) would move your goals forward.",
        "uz-Latn": "Oyiga {saving} so'm (kirimning 10%) jamg'arish maqsadlaringizni "
                   "yaqinlashtiradi.",
        "ru": "Откладывая {saving} сум в месяц (10% дохода), вы быстрее достигнете целей.",
        "kk": "Айына {saving} сум (кірістің 10%) жинау мақсаттарыңызды жақындатады.",
        "tr": "Ayda {saving} UZS (gelirin %10'u) biriktirmek hedeflerinizi hızlandırır."},
    "insight.teaser": {
        "en": "You could save {saving} UZS this month",
        "uz-Latn": "Bu oy {saving} so'm tejash mumkin",
        "ru": "В этом месяце можно сэкономить {saving} сум",
        "kk": "Осы айда {saving} сум үнемдеуге болады",
        "tr": "Bu ay {saving} UZS tasarruf edebilirsiniz"},

    # AI savol-javob (BE-903)
    "ai.suggestion.1": {"en": "Where did most of my money go this month?",
                        "uz-Latn": "Bu oy pulim eng ko'p nimaga ketdi?",
                        "ru": "На что ушло больше всего денег в этом месяце?",
                        "kk": "Осы айда ақшам көбіне неге кетті?",
                        "tr": "Bu ay param en çok nereye gitti?"},
    "ai.suggestion.2": {"en": "How can I spend less on food?",
                        "uz-Latn": "Ovqatga qanday qilib kamroq sarflayman?",
                        "ru": "Как тратить меньше на еду?",
                        "kk": "Тамаққа қалай аз жұмсаймын?",
                        "tr": "Yemeğe nasıl daha az harcarım?"},
    "ai.suggestion.3": {"en": "Am I on track with my goals?",
                        "uz-Latn": "Maqsadlarimga yetib boryapmanmi?",
                        "ru": "Успеваю ли я к своим целям?",
                        "kk": "Мақсаттарыма жетіп жатырмын ба?",
                        "tr": "Hedeflerime doğru ilerliyor muyum?"},
    "ai.suggestion.4": {"en": "Which budget am I close to exceeding?",
                        "uz-Latn": "Qaysi byudjetim oshib ketishga yaqin?",
                        "ru": "Какой бюджет я скоро превышу?",
                        "kk": "Қай бюджетім асып кетуге жақын?",
                        "tr": "Hangi bütçemi aşmak üzereyim?"},
    "ai.no_data": {"en": "No expenses in the last {days} days yet. Start adding transactions.",
                   "uz-Latn": "Oxirgi {days} kunda xarajat yo'q. Tranzaksiyalarni kiritishni "
                              "boshlang.",
                   "ru": "За последние {days} дней расходов нет. Начните добавлять операции.",
                   "kk": "Соңғы {days} күнде шығыс жоқ. Операцияларды енгізуді бастаңыз.",
                   "tr": "Son {days} günde harcama yok. İşlem eklemeye başlayın."},
    "ai.summary": {"en": "In the last {days} days you spent {total} UZS. The biggest share: "
                         "{category} ({share}%). Consider a monthly budget for it.",
                   "uz-Latn": "Oxirgi {days} kunda jami xarajat {total} so'm. Eng katta ulush: "
                              "{category} ({share}%). Shu kategoriya uchun oylik byudjet "
                              "belgilashni ko'rib chiqing.",
                   "ru": "За последние {days} дней расходы составили {total} сум. Больше всего: "
                         "{category} ({share}%). Попробуйте задать для неё месячный бюджет.",
                   "kk": "Соңғы {days} күнде барлығы {total} сум жұмсалды. Ең үлкен үлес: "
                         "{category} ({share}%). Оған айлық бюджет қойып көріңіз.",
                   "tr": "Son {days} günde toplam {total} UZS harcadınız. En büyük pay: "
                         "{category} (%{share}). Bunun için aylık bütçe belirleyin."},
}

class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def t(key: str, locale: str | None = None, **params: Any) -> str:
    lang = locale or locale_ctx.get()
    entry = _C.get(key)
    if entry is None:
        return key
    if lang == "uz-Cyrl":
        text = latin_to_cyrillic(entry.get("uz-Latn", entry["en"]))
    else:
        text = entry.get(lang) or entry["en"]
    return text.format_map(_SafeDict(params)) if params else text


def has_key(key: str) -> bool:
    return key in _C


def format_amount(amount: int) -> str:
    """12500000 -> "12 500 000" (dizayndagi tabular format)."""
    sign = "-" if amount < 0 else ""
    return sign + f"{abs(amount):,}".replace(",", " ")
