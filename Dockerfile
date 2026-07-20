FROM python:3.12.11-slim-bookworm AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY pyproject.toml README.md ./
COPY apps/api/src ./apps/api/src
RUN python -m pip install --prefix=/install .

FROM python:3.12.11-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd --system --gid 10001 aegisx && useradd --system --uid 10001 --gid aegisx --create-home aegisx
COPY --from=builder /install /usr/local
WORKDIR /app
COPY alembic.ini ./alembic.ini
COPY apps/api/migrations ./apps/api/migrations
USER 10001:10001
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn aegisx.api:app --host 0.0.0.0 --port 8000 --no-access-log"]
