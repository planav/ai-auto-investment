# ── Build stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS base

WORKDIR /app

# Install OS dependencies needed by some Python packages (psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# ── Runtime stage ────────────────────────────────────────────────────────────
FROM base AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
