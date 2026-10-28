FROM ghcr.io/astral-sh/uv:0.13.5 AS uv
FROM python:3.13.17-slim-bookworm

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Dependency layer: only changes when pyproject.toml / uv.lock change.
# --only-group api installs the API packages, not pandas/scikit-learn.
COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --only-group api --no-install-project

# Run Uvicorn straight from the virtual environment; uv is not needed at runtime.
ENV PATH="/app/.venv/bin:$PATH"

COPY api ./api

# Do not run as root inside the container.
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
