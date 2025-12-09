FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Установим poetry
RUN pip install --no-cache-dir poetry

# Скопируем pyproject и установим зависимости
COPY pyproject.toml README.md ./
RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-root --no-interaction --no-ansi

# Скопируем исходники
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Переменные окружения по умолчанию
ENV APP_ENV=production \
    APP_DEBUG=false

# Команда старта: миграции + uvicorn
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000