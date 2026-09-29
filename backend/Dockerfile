# Finora backend. Non-root, faqat runtime bog'liqliklar, secret'lar image'ga kirmaydi.
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.8 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./

FROM python:3.12-slim
# PDF eksport uchun Unicode shrift (kirill, o'zbek harflari) — BE-602
RUN apt-get update \
    && apt-get install -y --no-install-recommends fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
RUN useradd --system --uid 10001 --home-dir /app finora
WORKDIR /app
COPY --from=build --chown=root:root /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 FINORA_ENV=prod \
    FINORA_PDF_FONT_PATH=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
USER 10001
EXPOSE 8000
# --proxy-headers: client IP va proto faqat ishonchli gateway'dan (FORWARDED_ALLOW_IPS)
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", \
     "--proxy-headers", "--no-server-header"]
