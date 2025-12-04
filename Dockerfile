# Stage 1: Builder - install Python deps
FROM python:3.11-slim AS builder
WORKDIR /app

# copy requirements first to take advantage of layer caching
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# Install system deps (cron, tzdata)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y cron tzdata && \
    rm -rf /var/lib/apt/lists/*

# Copy installed python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . /app

# Make sure Python sees /app modules
ENV PYTHONPATH=/app

# Ensure cron script is executable and install crontab
RUN chmod 755 /app/cron/log_2fa_cron.py && \
    chmod 644 /app/cron/2fa-cron && \
    crontab /app/cron/2fa-cron

# Create persistent mount points
RUN mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

# Start cron and the FastAPI app (uvicorn)
CMD service cron start && uvicorn app:app --host 0.0.0.0 --port 8080
