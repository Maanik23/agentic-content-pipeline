FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS deps
COPY pyproject.toml .
RUN pip install --no-cache-dir .

FROM deps AS app
COPY src/ src/
COPY examples/ examples/

EXPOSE 8000
CMD ["uvicorn", "pipeline.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
