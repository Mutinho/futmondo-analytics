# Backend Dockerfile - FastAPI
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including cron)
RUN apt-get update && apt-get install -y \
    curl \
    sqlite3 \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data and static files
RUN mkdir -p /app/data /app/static/photos/players

# Create crontab file for daily sync at 02:00 AM
RUN echo "0 2 * * * cd /app && /usr/local/bin/python scripts/sync_data.py >> /var/log/sync_data.log 2>&1" > /etc/cron.d/futmondo-sync
RUN chmod 0644 /etc/cron.d/futmondo-sync
RUN crontab /etc/cron.d/futmondo-sync

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run entrypoint script
CMD ["/app/entrypoint.sh"]

