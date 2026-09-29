"""OpenAPI spetsifikatsiyasini faylga yozish (BE-1901) — Flutter client generatsiyasi uchun.

    uv run python -m app.openapi ../docs/backend/openapi.json          # yozish
    uv run python -m app.openapi ../docs/backend/openapi.json --check  # CI: eskirganmi

Prod'da Swagger UI o'chiq; spetsifikatsiya repoda versiyalanadi.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.core.config import Settings


def build_spec() -> dict[str, Any]:
    from app.main import create_app

    # _env_file=None: lokal .env ta'sir qilmasin (spetsifikatsiya deterministik)
    settings = Settings(_env_file=None,
                        env="test", database_url="sqlite+aiosqlite:///:memory:",
                        redis_url=None, docs_enabled=True)
    app = create_app(settings)
    spec = app.openapi()
    spec["info"]["description"] = (
        "Finora API v1. Barcha vaqtlar ISO 8601 UTC; mijoz vaqt zonasi `X-Timezone` "
        "sarlavhasida. Summalar — so'm (butun son). Xato formati: "
        "`{code, message, request_id}` (+ `fields`, `retry_after`, `attempts_left`). "
        "Yozuv yaratuvchi POST'lar `Idempotency-Key` talab qiladi. "
        "Xato kodlari: docs/backend/ERROR_CODES.md."
    )
    return spec


def render() -> str:
    return json.dumps(build_spec(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m app.openapi")
    parser.add_argument("path", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    if args.check:
        current = args.path.read_text(encoding="utf-8") if args.path.exists() else ""
        if current != text:
            sys.stderr.write(f"{args.path} eskirgan: `python -m app.openapi {args.path}`\n")
            return 1
        return 0
    args.path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
