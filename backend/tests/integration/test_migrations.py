"""b7c1e4d2a9f0 data-migratsiyasi: eski ma'lumotlar yo'qolmaydi va yangi modelga o'tadi."""

import sqlite3
import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config

BACKEND = Path(__file__).resolve().parents[2]


def _cfg(db: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    monkeypatch.setenv("FINORA_MIGRATIONS_DATABASE_URL", f"sqlite+aiosqlite:///{db}")
    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "migrations"))
    return cfg


def test_legacy_data_is_migrated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "legacy.db"
    cfg = _cfg(db, monkeypatch)
    command.upgrade(cfg, "5a24b90a75ad")

    u = uuid.uuid4().hex
    ts = "2026-09-20 10:00:00.000000+00:00"
    con = sqlite3.connect(db)
    con.execute("INSERT INTO users (id, phone_ciphertext, phone_index, created_at) "
                "VALUES (?, x'00', 'idx', ?)", (u, ts))
    rows = [("expense", 5000, "Taksi"), ("expense", 7000, "Kitoblar"),
            ("income", 900000, "Maosh"), ("expense", 1000, "kitoblar")]
    for kind, amount, category in rows:
        con.execute("INSERT INTO transactions (id, user_id, kind, amount, category, note, "
                    "occurred_at, created_at) VALUES (?, ?, ?, ?, ?, NULL, ?, ?)",
                    (uuid.uuid4().hex, u, kind, amount, category, ts, ts))
    con.execute("INSERT INTO budgets (id, user_id, category, monthly_limit, created_at) "
                "VALUES (?, ?, 'Oziq-ovqat', 800000, ?)", (uuid.uuid4().hex, u, ts))
    con.execute("INSERT INTO reminders (id, user_id, title, amount, due_at, repeat, created_at) "
                "VALUES (?, ?, 'Gaz', NULL, '2026-09-30 20:00:00.000000+00:00', 'none', ?)",
                (uuid.uuid4().hex, u, ts))
    con.execute("INSERT INTO notifications (id, user_id, kind, title, body, created_at) "
                "VALUES (?, ?, 'new_sign_in', 't', 'b', ?)", (uuid.uuid4().hex, u, ts))
    con.commit()
    con.close()

    command.upgrade(cfg, "head")

    con = sqlite3.connect(db)
    accounts = con.execute("SELECT type, name, is_default, opening_balance "
                           "FROM accounts").fetchall()
    assert accounts == [("cash", "Cash", 1, 0)]
    txs = con.execute("SELECT type, category_id FROM transactions ORDER BY amount").fetchall()
    user_cats = dict(con.execute("SELECT name_key, id FROM categories").fetchall())
    assert set(user_cats) == {"kitoblar"}  # "Kitoblar" va "kitoblar" — bitta kategoriya
    kit = user_cats["kitoblar"]
    kit_hex = uuid.UUID(bytes=kit).hex if isinstance(kit, bytes) else uuid.UUID(kit).hex
    assert [t for t, _ in txs] == ["expense", "expense", "expense", "income"]
    by_cat = [c for _, c in txs]
    assert by_cat[1] == "transport" and by_cat[3] == "salary"
    assert uuid.UUID(by_cat[0]).hex == kit_hex == uuid.UUID(by_cat[2]).hex
    assert con.execute("SELECT category_id, monthly_limit FROM category_prefs").fetchall() == \
        [("groceries", 800000)]
    assert con.execute("SELECT next_due_date, repeat, enabled, amount FROM reminders"
                       ).fetchall() == [("2026-10-01", "once", 0, 1)]  # 01:00 Toshkent
    assert con.execute("SELECT type, deep_link FROM notifications").fetchall() == \
        [("security", "/profile")]
    con.close()
