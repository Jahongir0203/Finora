from app.core.i18n import (
    _C,
    SUPPORTED_LANGUAGES,
    latin_to_cyrillic,
    normalize_language,
    parse_accept_language,
    t,
)


def test_every_key_has_all_written_languages():
    for key, entry in _C.items():
        assert {"en", "uz-Latn", "ru", "kk", "tr"} <= set(entry), key


def test_placeholders_match_across_languages():
    import re

    for key, entry in _C.items():
        names = {lang: set(re.findall(r"\{(\w+)\}", text)) for lang, text in entry.items()}
        assert len({frozenset(v) for v in names.values()}) == 1, (key, names)


def test_language_negotiation():
    assert normalize_language("uz-UZ") == "uz-Latn"
    assert normalize_language("uz_Cyrl_UZ") == "uz-Cyrl"
    assert normalize_language("kz") == "kk"
    assert normalize_language("de") is None
    assert parse_accept_language("de-DE,ru;q=0.8,en;q=0.9") == "en"
    assert parse_accept_language("") is None
    assert set(SUPPORTED_LANGUAGES) == {"en", "uz-Latn", "uz-Cyrl", "ru", "kk", "tr"}


def test_uzbek_cyrillic_transliteration():
    assert latin_to_cyrillic("O'zbekiston") == "Ўзбекистон"
    assert latin_to_cyrillic("G'alaba, shoshilmang") == "Ғалаба, шошилманг"
    assert latin_to_cyrillic("Eslatma {title}") == "Эслатма {title}"  # placeholder saqlanadi
    assert t("category.groceries", "uz-Cyrl") == "Озиқ-овқат"
    assert t("notif.goal_milestone.title", "uz-Cyrl", goal="Car", pct=50) == \
        "Car: 50% га етдингиз"


def test_fallbacks():
    assert t("category.food", "de") == "Food & drinks"
    assert t("no.such.key") == "no.such.key"
    assert t("notif.budget.body", "en", spent="1") == "Spent 1 of {limit} UZS this month"
