# Build context: repository root (the API serves ../content).
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project --extra neural

COPY backend/app ./app
COPY backend/scripts ./scripts
COPY content /app/content

RUN useradd --create-home explodeai && mkdir -p /app/backend/data && chown -R explodeai /app/backend/data
USER explodeai

# Lesson 03 runs a small local embedding model (downloaded once on first use, free, no key).
ENV FASTEMBED_CACHE_PATH=/app/backend/data/fastembed

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
