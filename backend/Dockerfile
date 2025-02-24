FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -s /bin/bash -d /app appuser && \
    chown -R appuser:appgroup /app

# Copy minimal requirements for faster initial setup
COPY --chown=appuser:appgroup backend/requirements.minimal.txt .

# Create and activate virtual environment
RUN python -m venv /opt/venv && \
    chown -R appuser:appgroup /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

USER appuser

# Install dependencies with wheel caching
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install --no-cache-dir -r requirements.minimal.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Create non-root user in final stage
RUN groupadd -r appgroup && \
    useradd -r -g appgroup -s /bin/bash -d /app appuser && \
    chown -R appuser:appgroup /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application
COPY --chown=appuser:appgroup backend/ .

USER appuser

EXPOSE 5000
CMD ["python", "app.py"]