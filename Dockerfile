# Multi-stage build for ephemeris-agpl-service

# Stage 1: Download Swiss Ephemeris data files
FROM alpine:latest AS sweph-downloader

RUN apk add --no-cache curl

# Download Swiss Ephemeris planetary and lunar data files
# Source: https://www.astro.com/ftp/swisseph/ephe/
RUN mkdir -p /sweph && \
    cd /sweph && \
    curl -L "https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1" -o sepl_18.se1 && \
    curl -L "https://www.astro.com/ftp/swisseph/ephe/semo_18.se1" -o semo_18.se1 && \
    ls -la /sweph

# Stage 2: Python application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Swiss Ephemeris data files from downloader stage
# If using volume mount, this can be skipped
COPY --from=sweph-downloader /sweph /app/sweph

# Copy requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY app/ ./app/

# Set environment variables
ENV SWEPH_PATH=/app/sweph
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Build arguments for version info
ARG GIT_COMMIT=unknown
ARG BUILD_TAG=dev
ARG BUILD_TIME_UTC=unknown

# Set build info as environment variables
ENV GIT_COMMIT=${GIT_COMMIT}
ENV BUILD_TAG=${BUILD_TAG}
ENV BUILD_TIME_UTC=${BUILD_TIME_UTC}

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')"

# Run application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
