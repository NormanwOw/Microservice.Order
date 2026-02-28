FROM ghcr.io/astral-sh/uv:python3.14-bookworm AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv venv && uv sync --frozen --no-cache

FROM python:3.14-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir /app/logs || true

COPY --from=builder /app/.venv /app/.venv

COPY src/ ./src/
COPY alembic.ini .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1