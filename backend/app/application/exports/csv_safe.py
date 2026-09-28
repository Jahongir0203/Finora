"""CSV/Excel formula injection himoyasi (02-backend.md, 6-bo'lim)."""

import csv
import io
from collections.abc import Iterable, Sequence

_DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sanitize_cell(value: object) -> str:
    text = "" if value is None else str(value)
    if text.startswith(_DANGEROUS_PREFIXES):
        return "'" + text
    return text


def render_csv(header: Sequence[str], rows: Iterable[Sequence[object]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    writer.writerow([sanitize_cell(h) for h in header])
    for row in rows:
        writer.writerow([sanitize_cell(c) for c in row])
    # Excel UTF-8'ni to'g'ri ochishi uchun BOM
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")
