# Stage 1: Base - Common foundation
FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Stage 2: Development - For local work with hot-reload
FROM base AS development
# Re-install dependencies globally for easier dev work
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Code stays outside (mounted via volumes) or copied
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Builder - For installing production dependencies
FROM base AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 4: Production - Minimal and secure runtime
FROM base AS production
# Non-root user for security
RUN groupadd -r agent && useradd -r -g agent -d /app agent

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code and assets
COPY app/ ./app/
COPY utils/ ./utils/
COPY static/ ./static/
COPY nginx.conf .

RUN chown -R agent:agent /app
USER agent

EXPOSE 8000

# Health check using the internal endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
